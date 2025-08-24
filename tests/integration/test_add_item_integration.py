import json
from decimal import Decimal
from moto import mock_aws
import boto3
from presentation.handlers.add_item_handler import lambda_handler


@mock_aws
class TestAddItemIntegration:
    """Integration test demonstrating the complete add item to cart flow."""
    
    def test_complete_add_item_flow(self):
        """Test the complete flow from Lambda handler to DynamoDB."""
        # Setup mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='shopping-carts',
            KeySchema=[{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Test adding first item to new cart
        event1 = {
            'body': json.dumps({
                'customer_id': 'customer-integration-test',
                'product_id': 'prod-laptop',
                'product_name': 'Gaming Laptop',
                'price': '1299.99',
                'quantity': 1
            })
        }
        
        response1 = lambda_handler(event1, {})
        
        # Verify first item addition
        assert response1['statusCode'] == 200
        body1 = json.loads(response1['body'])
        assert body1['success'] is True
        assert body1['cart']['customer_id'] == 'customer-integration-test'
        assert body1['cart']['total_items'] == 1
        assert body1['cart']['subtotal'] == '1299.99'
        assert len(body1['cart']['items']) == 1
        assert body1['cart']['items'][0]['product_name'] == 'Gaming Laptop'
        
        # Test adding second item to existing cart
        event2 = {
            'body': json.dumps({
                'customer_id': 'customer-integration-test',
                'product_id': 'prod-mouse',
                'product_name': 'Wireless Mouse',
                'price': '49.99',
                'quantity': 2
            })
        }
        
        response2 = lambda_handler(event2, {})
        
        # Verify second item addition
        assert response2['statusCode'] == 200
        body2 = json.loads(response2['body'])
        assert body2['success'] is True
        assert body2['cart']['customer_id'] == 'customer-integration-test'
        assert body2['cart']['total_items'] == 3  # 1 laptop + 2 mice
        assert body2['cart']['subtotal'] == '1399.97'  # 1299.99 + (49.99 * 2)
        assert len(body2['cart']['items']) == 2
        
        # Verify both items are in cart
        items = {item['product_id']: item for item in body2['cart']['items']}
        assert 'prod-laptop' in items
        assert 'prod-mouse' in items
        assert items['prod-laptop']['quantity'] == 1
        assert items['prod-mouse']['quantity'] == 2
        
        # Test adding same item again (should update quantity)
        event3 = {
            'body': json.dumps({
                'customer_id': 'customer-integration-test',
                'product_id': 'prod-laptop',
                'product_name': 'Gaming Laptop',
                'price': '1299.99',
                'quantity': 1
            })
        }
        
        response3 = lambda_handler(event3, {})
        
        # Verify quantity update
        assert response3['statusCode'] == 200
        body3 = json.loads(response3['body'])
        assert body3['success'] is True
        assert body3['cart']['total_items'] == 4  # 2 laptops + 2 mice
        assert body3['cart']['subtotal'] == '2699.96'  # (1299.99 * 2) + (49.99 * 2)
        assert len(body3['cart']['items']) == 2  # Still only 2 unique products
        
        # Verify laptop quantity was updated
        items = {item['product_id']: item for item in body3['cart']['items']}
        assert items['prod-laptop']['quantity'] == 2
        assert items['prod-mouse']['quantity'] == 2
    
    def test_error_handling_integration(self):
        """Test error handling in the complete flow."""
        # Setup mock DynamoDB table
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='shopping-carts',
            KeySchema=[{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Test invalid quantity
        event = {
            'body': json.dumps({
                'customer_id': 'customer-error-test',
                'product_id': 'prod-invalid',
                'product_name': 'Invalid Product',
                'price': '10.00',
                'quantity': 0  # Invalid quantity
            })
        }
        
        response = lambda_handler(event, {})
        
        # Verify error response
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'Quantity must be greater than 0' in body['error']
