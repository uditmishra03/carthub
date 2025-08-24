import json
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from presentation.handlers.add_item_handler import lambda_handler


class TestAddItemLambdaHandler:
    def test_add_item_success(self):
        # Arrange
        event = {
            'body': json.dumps({
                'customer_id': 'customer-123',
                'product_id': 'prod-123',
                'product_name': 'Test Product',
                'price': '29.99',
                'quantity': 2
            })
        }
        context = {}
        
        # Act
        with patch('presentation.handlers.add_item_handler.get_add_item_use_case') as mock_get_use_case:
            mock_use_case = Mock()
            mock_get_use_case.return_value = mock_use_case
            
            # Mock successful response
            from domain.entities.cart import Cart
            from domain.entities.cart_item import CartItem
            from application.use_cases.add_item_to_cart import AddItemResponse
            
            cart = Cart(customer_id='customer-123')
            cart_item = CartItem(
                product_id='prod-123',
                product_name='Test Product',
                price=Decimal('29.99'),
                quantity=2
            )
            cart.add_item(cart_item)
            
            mock_use_case.execute.return_value = AddItemResponse(success=True, cart=cart)
            
            response = lambda_handler(event, context)
        
        # Assert
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['cart']['customer_id'] == 'customer-123'
        assert body['cart']['total_items'] == 2
        assert body['cart']['subtotal'] == '59.98'
        assert len(body['cart']['items']) == 1
    
    def test_add_item_invalid_request_body(self):
        # Arrange
        event = {
            'body': 'invalid json'
        }
        context = {}
        
        # Act
        response = lambda_handler(event, context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'Invalid request body' in body['error']
    
    def test_add_item_missing_required_fields(self):
        # Arrange
        event = {
            'body': json.dumps({
                'customer_id': 'customer-123',
                # Missing required fields
            })
        }
        context = {}
        
        # Act
        response = lambda_handler(event, context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'Missing required field' in body['error']
    
    def test_add_item_use_case_failure(self):
        # Arrange
        event = {
            'body': json.dumps({
                'customer_id': 'customer-123',
                'product_id': 'prod-123',
                'product_name': 'Test Product',
                'price': '29.99',
                'quantity': 0  # Invalid quantity
            })
        }
        context = {}
        
        # Act
        with patch('presentation.handlers.add_item_handler.get_add_item_use_case') as mock_get_use_case:
            mock_use_case = Mock()
            mock_get_use_case.return_value = mock_use_case
            
            from application.use_cases.add_item_to_cart import AddItemResponse
            mock_use_case.execute.return_value = AddItemResponse(
                success=False, 
                error_message="Quantity must be greater than 0"
            )
            
            response = lambda_handler(event, context)
        
        # Assert
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error'] == "Quantity must be greater than 0"
    
    def test_add_item_internal_server_error(self):
        # Arrange
        event = {
            'body': json.dumps({
                'customer_id': 'customer-123',
                'product_id': 'prod-123',
                'product_name': 'Test Product',
                'price': '29.99',
                'quantity': 2
            })
        }
        context = {}
        
        # Act
        with patch('presentation.handlers.add_item_handler.get_add_item_use_case') as mock_get_use_case:
            mock_get_use_case.side_effect = Exception("Database connection failed")
            
            response = lambda_handler(event, context)
        
        # Assert
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'Internal server error' in body['error']
