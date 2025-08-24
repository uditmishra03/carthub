import pytest
from decimal import Decimal
from domain.entities.cart_item import CartItem


class TestCartItem:
    def test_create_cart_item_with_valid_data(self):
        # Arrange
        product_id = "prod-123"
        product_name = "Test Product"
        price = Decimal("29.99")
        quantity = 2
        
        # Act
        cart_item = CartItem(
            product_id=product_id,
            product_name=product_name,
            price=price,
            quantity=quantity
        )
        
        # Assert
        assert cart_item.product_id == product_id
        assert cart_item.product_name == product_name
        assert cart_item.price == price
        assert cart_item.quantity == quantity
        assert cart_item.subtotal == Decimal("59.98")
    
    def test_cart_item_subtotal_calculation(self):
        # Arrange & Act
        cart_item = CartItem(
            product_id="prod-456",
            product_name="Another Product",
            price=Decimal("15.50"),
            quantity=3
        )
        
        # Assert
        assert cart_item.subtotal == Decimal("46.50")
    
    def test_cart_item_with_zero_quantity_raises_error(self):
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Quantity must be greater than 0"):
            CartItem(
                product_id="prod-789",
                product_name="Test Product",
                price=Decimal("10.00"),
                quantity=0
            )
    
    def test_cart_item_with_negative_price_raises_error(self):
        # Arrange, Act & Assert
        with pytest.raises(ValueError, match="Price must be greater than or equal to 0"):
            CartItem(
                product_id="prod-789",
                product_name="Test Product",
                price=Decimal("-5.00"),
                quantity=1
            )
    
    def test_update_quantity(self):
        # Arrange
        cart_item = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("10.00"),
            quantity=1
        )
        
        # Act
        cart_item.update_quantity(5)
        
        # Assert
        assert cart_item.quantity == 5
        assert cart_item.subtotal == Decimal("50.00")
    
    def test_update_quantity_with_invalid_value_raises_error(self):
        # Arrange
        cart_item = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("10.00"),
            quantity=1
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Quantity must be greater than 0"):
            cart_item.update_quantity(0)
