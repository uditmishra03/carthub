"""
Comprehensive Backend API Tests for Shopping Cart Application
Tests all API endpoints with various scenarios including edge cases
"""

import pytest
import requests
import json
from decimal import Decimal
from datetime import datetime
import uuid
import time


class TestBackendAPI:
    """Test suite for backend API endpoints."""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Base URL for API testing."""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def test_customer_id(self):
        """Generate unique customer ID for testing."""
        return f"test-customer-{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture(scope="class")
    def sample_product(self):
        """Sample product data for testing."""
        return {
            "product_id": f"prod-{uuid.uuid4().hex[:8]}",
            "product_name": "Test Gaming Laptop",
            "price": "1299.99",
            "quantity": 1
        }
    
    def test_health_check_endpoint(self, api_base_url):
        """Test health check endpoint."""
        response = requests.get(f"{api_base_url}/health/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "database" in data
        assert data["version"] == "2.0.0"
    
    def test_readiness_check_endpoint(self, api_base_url):
        """Test readiness check endpoint."""
        response = requests.get(f"{api_base_url}/health/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
    
    def test_liveness_check_endpoint(self, api_base_url):
        """Test liveness check endpoint."""
        response = requests.get(f"{api_base_url}/health/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
    
    def test_add_item_to_cart_success(self, api_base_url, test_customer_id, sample_product):
        """Test successfully adding item to cart."""
        payload = {
            "customer_id": test_customer_id,
            **sample_product
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert "cart" in data
        
        cart = data["cart"]
        assert cart["customer_id"] == test_customer_id
        assert cart["total_items"] == 1
        assert len(cart["items"]) == 1
        
        item = cart["items"][0]
        assert item["product_id"] == sample_product["product_id"]
        assert item["product_name"] == sample_product["product_name"]
        assert float(item["price"]) == float(sample_product["price"])
        assert item["quantity"] == sample_product["quantity"]
    
    def test_add_item_invalid_price(self, api_base_url, test_customer_id):
        """Test adding item with invalid price."""
        payload = {
            "customer_id": test_customer_id,
            "product_id": "invalid-prod",
            "product_name": "Invalid Product",
            "price": "-10.00",  # Invalid negative price
            "quantity": 1
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_add_item_invalid_quantity(self, api_base_url, test_customer_id):
        """Test adding item with invalid quantity."""
        payload = {
            "customer_id": test_customer_id,
            "product_id": "invalid-prod",
            "product_name": "Invalid Product",
            "price": "10.00",
            "quantity": 0  # Invalid zero quantity
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_add_item_missing_fields(self, api_base_url):
        """Test adding item with missing required fields."""
        payload = {
            "customer_id": "test-customer",
            # Missing product_id, product_name, price, quantity
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_get_cart_success(self, api_base_url, test_customer_id):
        """Test successfully retrieving cart."""
        response = requests.get(f"{api_base_url}/api/v1/cart/{test_customer_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "cart" in data
        
        cart = data["cart"]
        assert cart["customer_id"] == test_customer_id
        assert "total_items" in cart
        assert "subtotal" in cart
        assert "items" in cart
    
    def test_get_nonexistent_cart(self, api_base_url):
        """Test retrieving non-existent cart."""
        nonexistent_customer = f"nonexistent-{uuid.uuid4().hex[:8]}"
        response = requests.get(f"{api_base_url}/api/v1/cart/{nonexistent_customer}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        cart = data["cart"]
        assert cart["total_items"] == 0
        assert len(cart["items"]) == 0
    
    def test_update_item_quantity_success(self, api_base_url, test_customer_id, sample_product):
        """Test successfully updating item quantity."""
        # First add an item
        payload = {
            "customer_id": test_customer_id,
            **sample_product
        }
        requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        
        # Then update quantity
        new_quantity = 3
        response = requests.put(
            f"{api_base_url}/api/v1/cart/{test_customer_id}/items/{sample_product['product_id']}",
            params={"quantity": new_quantity}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        cart = data["cart"]
        
        # Find the updated item
        updated_item = next(
            (item for item in cart["items"] if item["product_id"] == sample_product["product_id"]),
            None
        )
        assert updated_item is not None
        assert updated_item["quantity"] == new_quantity
    
    def test_update_item_quantity_negative(self, api_base_url, test_customer_id, sample_product):
        """Test updating item quantity with negative value."""
        response = requests.put(
            f"{api_base_url}/api/v1/cart/{test_customer_id}/items/{sample_product['product_id']}",
            params={"quantity": -1}
        )
        
        assert response.status_code == 400  # Bad request
    
    def test_remove_item_from_cart_success(self, api_base_url, test_customer_id, sample_product):
        """Test successfully removing item from cart."""
        # First add an item
        payload = {
            "customer_id": test_customer_id,
            **sample_product
        }
        requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        
        # Then remove it
        response = requests.delete(
            f"{api_base_url}/api/v1/cart/{test_customer_id}/items/{sample_product['product_id']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        cart = data["cart"]
        
        # Verify item is removed
        removed_item = next(
            (item for item in cart["items"] if item["product_id"] == sample_product["product_id"]),
            None
        )
        assert removed_item is None
    
    def test_remove_nonexistent_item(self, api_base_url, test_customer_id):
        """Test removing non-existent item from cart."""
        nonexistent_product = f"nonexistent-{uuid.uuid4().hex[:8]}"
        response = requests.delete(
            f"{api_base_url}/api/v1/cart/{test_customer_id}/items/{nonexistent_product}"
        )
        
        assert response.status_code == 200  # Should handle gracefully
        data = response.json()
        assert data["success"] is True
    
    def test_clear_cart_success(self, api_base_url, test_customer_id, sample_product):
        """Test successfully clearing cart."""
        # First add an item
        payload = {
            "customer_id": test_customer_id,
            **sample_product
        }
        requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        
        # Then clear cart
        response = requests.delete(f"{api_base_url}/api/v1/cart/{test_customer_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
    
    def test_checkout_success(self, api_base_url, test_customer_id, sample_product):
        """Test successful checkout process."""
        # First add an item to cart
        payload = {
            "customer_id": test_customer_id,
            **sample_product
        }
        requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        
        # Then checkout
        checkout_payload = {
            "customer_id": test_customer_id,
            "payment_method": "credit_card",
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            }
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/checkout", json=checkout_payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "order_id" in data
        assert "total_amount" in data
        assert data["order_id"] is not None
    
    def test_checkout_empty_cart(self, api_base_url):
        """Test checkout with empty cart."""
        empty_customer = f"empty-{uuid.uuid4().hex[:8]}"
        checkout_payload = {
            "customer_id": empty_customer,
            "payment_method": "credit_card",
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            }
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/checkout", json=checkout_payload)
        
        assert response.status_code == 400  # Bad request for empty cart
    
    def test_api_response_time(self, api_base_url):
        """Test API response time performance."""
        start_time = time.time()
        response = requests.get(f"{api_base_url}/health/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
        assert response.status_code == 200
    
    @pytest.mark.parametrize("quantity", [1, 5, 10, 100])
    def test_add_multiple_quantities(self, api_base_url, test_customer_id, quantity):
        """Test adding items with different quantities."""
        product = {
            "product_id": f"prod-qty-{quantity}-{uuid.uuid4().hex[:4]}",
            "product_name": f"Test Product Qty {quantity}",
            "price": "10.00",
            "quantity": quantity
        }
        
        payload = {
            "customer_id": test_customer_id,
            **product
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/items", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        cart = data["cart"]
        
        # Find the added item
        added_item = next(
            (item for item in cart["items"] if item["product_id"] == product["product_id"]),
            None
        )
        assert added_item is not None
        assert added_item["quantity"] == quantity
    
    def test_concurrent_cart_operations(self, api_base_url):
        """Test concurrent operations on different carts."""
        customer1 = f"concurrent1-{uuid.uuid4().hex[:8]}"
        customer2 = f"concurrent2-{uuid.uuid4().hex[:8]}"
        
        product1 = {
            "customer_id": customer1,
            "product_id": "concurrent-prod-1",
            "product_name": "Concurrent Product 1",
            "price": "25.00",
            "quantity": 2
        }
        
        product2 = {
            "customer_id": customer2,
            "product_id": "concurrent-prod-2",
            "product_name": "Concurrent Product 2",
            "price": "35.00",
            "quantity": 3
        }
        
        # Add items to both carts
        response1 = requests.post(f"{api_base_url}/api/v1/cart/items", json=product1)
        response2 = requests.post(f"{api_base_url}/api/v1/cart/items", json=product2)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both carts are independent
        cart1_response = requests.get(f"{api_base_url}/api/v1/cart/{customer1}")
        cart2_response = requests.get(f"{api_base_url}/api/v1/cart/{customer2}")
        
        assert cart1_response.status_code == 200
        assert cart2_response.status_code == 200
        
        cart1_data = cart1_response.json()["cart"]
        cart2_data = cart2_response.json()["cart"]
        
        assert cart1_data["customer_id"] == customer1
        assert cart2_data["customer_id"] == customer2
        assert len(cart1_data["items"]) == 1
        assert len(cart2_data["items"]) == 1
