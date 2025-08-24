import pytest
from decimal import Decimal
from unittest.mock import Mock
from application.use_cases.add_item_to_cart import AddItemToCart, AddItemRequest
from application.interfaces.cart_repository import CartRepository
from domain.entities.cart import Cart
from domain.entities.cart_item import CartItem


class TestAddItemToCart:
    @pytest.fixture
    def mock_cart_repository(self):
        return Mock(spec=CartRepository)
    
    @pytest.fixture
    def add_item_use_case(self, mock_cart_repository):
        return AddItemToCart(cart_repository=mock_cart_repository)
    
    def test_add_item_to_new_cart(self, add_item_use_case, mock_cart_repository):
        # Arrange
        customer_id = "customer-123"
        request = AddItemRequest(
            customer_id=customer_id,
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("29.99"),
            quantity=2
        )
        
        mock_cart_repository.get_cart.return_value = None
        
        # Act
        result = add_item_use_case.execute(request)
        
        # Assert
        assert result.success is True
        assert result.cart.customer_id == customer_id
        assert len(result.cart.items) == 1
        assert result.cart.items[0].product_id == "prod-123"
        assert result.cart.items[0].quantity == 2
        assert result.cart.total_items == 2
        assert result.cart.subtotal == Decimal("59.98")
        
        # Verify repository calls
        mock_cart_repository.get_cart.assert_called_once_with(customer_id)
        mock_cart_repository.save_cart.assert_called_once()
    
    def test_add_item_to_existing_cart(self, add_item_use_case, mock_cart_repository):
        # Arrange
        customer_id = "customer-123"
        existing_cart = Cart(customer_id=customer_id)
        existing_item = CartItem(
            product_id="prod-456",
            product_name="Existing Product",
            price=Decimal("15.00"),
            quantity=1
        )
        existing_cart.add_item(existing_item)
        
        request = AddItemRequest(
            customer_id=customer_id,
            product_id="prod-123",
            product_name="New Product",
            price=Decimal("29.99"),
            quantity=2
        )
        
        mock_cart_repository.get_cart.return_value = existing_cart
        
        # Act
        result = add_item_use_case.execute(request)
        
        # Assert
        assert result.success is True
        assert result.cart.customer_id == customer_id
        assert len(result.cart.items) == 2
        assert result.cart.total_items == 3
        assert result.cart.subtotal == Decimal("74.98")  # 15.00 + 59.98
        
        # Verify repository calls
        mock_cart_repository.get_cart.assert_called_once_with(customer_id)
        mock_cart_repository.save_cart.assert_called_once()
    
    def test_add_same_item_to_existing_cart_updates_quantity(self, add_item_use_case, mock_cart_repository):
        # Arrange
        customer_id = "customer-123"
        existing_cart = Cart(customer_id=customer_id)
        existing_item = CartItem(
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("10.00"),
            quantity=1
        )
        existing_cart.add_item(existing_item)
        
        request = AddItemRequest(
            customer_id=customer_id,
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("10.00"),
            quantity=2
        )
        
        mock_cart_repository.get_cart.return_value = existing_cart
        
        # Act
        result = add_item_use_case.execute(request)
        
        # Assert
        assert result.success is True
        assert result.cart.customer_id == customer_id
        assert len(result.cart.items) == 1
        assert result.cart.items[0].quantity == 3  # 1 + 2
        assert result.cart.total_items == 3
        assert result.cart.subtotal == Decimal("30.00")
    
    def test_add_item_with_invalid_quantity_returns_error(self, add_item_use_case, mock_cart_repository):
        # Arrange
        request = AddItemRequest(
            customer_id="customer-123",
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("10.00"),
            quantity=0  # Invalid quantity
        )
        
        # Act
        result = add_item_use_case.execute(request)
        
        # Assert
        assert result.success is False
        assert "Quantity must be greater than 0" in result.error_message
        
        # Verify repository was not called
        mock_cart_repository.get_cart.assert_not_called()
        mock_cart_repository.save_cart.assert_not_called()
    
    def test_add_item_with_negative_price_returns_error(self, add_item_use_case, mock_cart_repository):
        # Arrange
        request = AddItemRequest(
            customer_id="customer-123",
            product_id="prod-123",
            product_name="Test Product",
            price=Decimal("-5.00"),  # Invalid price
            quantity=1
        )
        
        # Act
        result = add_item_use_case.execute(request)
        
        # Assert
        assert result.success is False
        assert "Price must be greater than or equal to 0" in result.error_message
        
        # Verify repository was not called
        mock_cart_repository.get_cart.assert_not_called()
        mock_cart_repository.save_cart.assert_not_called()
