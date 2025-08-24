import pytest
from decimal import Decimal
from domain.entities.cart import Cart
from domain.entities.cart_item import CartItem


class TestCart:
    def test_create_empty_cart(self):
        # Arrange & Act
        cart = Cart(customer_id="customer-123")
        
        # Assert
        assert cart.customer_id == "customer-123"
        assert cart.items == []
        assert cart.total_items == 0
        assert cart.subtotal == Decimal("0.00")
    
    def test_add_item_to_empty_cart(self):
        # Arrange
        cart = Cart(customer_id="customer-123")
        cart_item = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("29.99"),
            quantity=2
        )
        
        # Act
        cart.add_item(cart_item)
        
        # Assert
        assert len(cart.items) == 1
        assert cart.items[0] == cart_item
        assert cart.total_items == 2
        assert cart.subtotal == Decimal("59.98")
    
    def test_add_same_item_twice_updates_quantity(self):
        # Arrange
        cart = Cart(customer_id="customer-123")
        cart_item1 = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("10.00"),
            quantity=1
        )
        cart_item2 = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("10.00"),
            quantity=2
        )
        
        # Act
        cart.add_item(cart_item1)
        cart.add_item(cart_item2)
        
        # Assert
        assert len(cart.items) == 1
        assert cart.items[0].quantity == 3
        assert cart.total_items == 3
        assert cart.subtotal == Decimal("30.00")
    
    def test_add_different_items_to_cart(self):
        # Arrange
        cart = Cart(customer_id="customer-123")
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
        
        # Act
        cart.add_item(item1)
        cart.add_item(item2)
        
        # Assert
        assert len(cart.items) == 2
        assert cart.total_items == 3
        assert cart.subtotal == Decimal("50.00")
    
    def test_get_item_by_product_id(self):
        # Arrange
        cart = Cart(customer_id="customer-123")
        cart_item = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("29.99"),
            quantity=2
        )
        cart.add_item(cart_item)
        
        # Act
        found_item = cart.get_item_by_product_id("prod-123")
        
        # Assert
        assert found_item == cart_item
    
    def test_get_item_by_product_id_returns_none_when_not_found(self):
        # Arrange
        cart = Cart(customer_id="customer-123")
        
        # Act
        found_item = cart.get_item_by_product_id("non-existent")
        
        # Assert
        assert found_item is None
    
    def test_cart_details_dict(self):
        # Arrange
        cart = Cart(customer_id="customer-123")
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
        cart_details = cart.to_dict()
        
        # Assert
        expected = {
            "customer_id": "customer-123",
            "total_items": 3,
            "subtotal": "50.00",
            "items": [
                {
                    "product_id": "prod-123",
                    "product_name": "Product 1",
                    "price": "10.00",
                    "quantity": 1,
                    "subtotal": "10.00"
                },
                {
                    "product_id": "prod-456",
                    "product_name": "Product 2",
                    "price": "20.00",
                    "quantity": 2,
                    "subtotal": "40.00"
                }
            ]
        }
        assert cart_details == expected
