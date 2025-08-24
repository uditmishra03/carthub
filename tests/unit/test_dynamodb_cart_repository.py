import pytest
import boto3
from decimal import Decimal
from moto import mock_aws
from infrastructure.repositories.dynamodb_cart_repository import DynamoDBCartRepository
from domain.entities.cart import Cart
from domain.entities.cart_item import CartItem


class TestDynamoDBCartRepository:
    
    @mock_aws
    def test_get_cart_returns_none_when_not_found(self):
        # Arrange
        table_name = 'test-shopping-carts-1'
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        repository = DynamoDBCartRepository(table_name=table_name, region='us-east-1')
        
        # Act
        cart = repository.get_cart("non-existent-customer")
        
        # Assert
        assert cart is None
    
    @mock_aws
    def test_save_and_get_cart(self):
        # Arrange
        table_name = 'test-shopping-carts-2'
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        repository = DynamoDBCartRepository(table_name=table_name, region='us-east-1')
        
        cart = Cart(customer_id="customer-123")
        cart_item = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("29.99"),
            quantity=2
        )
        cart.add_item(cart_item)
        
        # Act - Save cart
        repository.save_cart(cart)
        
        # Act - Get cart
        retrieved_cart = repository.get_cart("customer-123")
        
        # Assert
        assert retrieved_cart is not None
        assert retrieved_cart.customer_id == "customer-123"
        assert len(retrieved_cart.items) == 1
        assert retrieved_cart.items[0].product_id == "prod-123"
        assert retrieved_cart.items[0].product_name == "Test Product"
        assert retrieved_cart.items[0].price == Decimal("29.99")
        assert retrieved_cart.items[0].quantity == 2
        assert retrieved_cart.total_items == 2
        assert retrieved_cart.subtotal == Decimal("59.98")
    
    @mock_aws
    def test_save_cart_with_multiple_items(self):
        # Arrange
        table_name = 'test-shopping-carts-3'
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        repository = DynamoDBCartRepository(table_name=table_name, region='us-east-1')
        
        cart = Cart(customer_id="customer-456")
        item1 = CartItem(
            product_id="prod-123",
            product_name="Product 1",
            price=Decimal("10.00"),
            quantity=1
        )
        item2 = CartItem(
            product_id="prod-456",
            product_name="Product 2",
            price=Decimal("20.00"),
            quantity=2
        )
        cart.add_item(item1)
        cart.add_item(item2)
        
        # Act
        repository.save_cart(cart)
        retrieved_cart = repository.get_cart("customer-456")
        
        # Assert
        assert retrieved_cart is not None
        assert len(retrieved_cart.items) == 2
        assert retrieved_cart.total_items == 3
        assert retrieved_cart.subtotal == Decimal("50.00")
    
    @mock_aws
    def test_update_existing_cart(self):
        # Arrange
        table_name = 'test-shopping-carts-4'
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'customer_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'customer_id', 'AttributeType': 'S'}],
            BillingMode='PAY_PER_REQUEST'
        )
        repository = DynamoDBCartRepository(table_name=table_name, region='us-east-1')
        
        # Save initial cart
        cart = Cart(customer_id="customer-789")
        initial_item = CartItem(
            product_id="prod-123",
            product_name="Initial Product",
            price=Decimal("15.00"),
            quantity=1
        )
        cart.add_item(initial_item)
        repository.save_cart(cart)
        
        # Act - Update cart with new item
        new_item = CartItem(
            product_id="prod-456",
            product_name="New Product",
            price=Decimal("25.00"),
            quantity=1
        )
        cart.add_item(new_item)
        repository.save_cart(cart)
        
        # Assert
        retrieved_cart = repository.get_cart("customer-789")
        assert retrieved_cart is not None
        assert len(retrieved_cart.items) == 2
        assert retrieved_cart.total_items == 2
        assert retrieved_cart.subtotal == Decimal("40.00")
