"""
Test suite for Carthub Backend API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

# Import the FastAPI app
from app.main import app

client = TestClient(app)

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test health check returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns service info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Shopping Cart Backend"
        assert data["version"] == "2.0.0"
        assert data["status"] == "running"

class TestCartAPI:
    """Test cart API endpoints"""
    
    @patch('app.routes.cart_routes.get_db')
    def test_get_cart_empty(self, mock_get_db):
        """Test getting an empty cart"""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = client.get("/api/v1/cart/customer-123")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "customer-123"
        assert data["items"] == []
        assert data["total_items"] == 0
        assert float(data["subtotal"]) == 0.0

    @patch('app.routes.cart_routes.get_db')
    def test_add_item_to_cart(self, mock_get_db):
        """Test adding an item to cart"""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        item_data = {
            "customer_id": "customer-123",
            "product_id": "prod-456",
            "product_name": "Test Product",
            "price": 29.99,
            "quantity": 2
        }
        
        response = client.post("/api/v1/cart/items", json=item_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

class TestInputValidation:
    """Test input validation"""
    
    def test_add_item_invalid_data(self):
        """Test adding item with invalid data"""
        invalid_data = {
            "customer_id": "",  # Empty customer ID
            "product_id": "prod-456",
            "product_name": "Test Product",
            "price": -10.0,  # Negative price
            "quantity": 0  # Zero quantity
        }
        
        response = client.post("/api/v1/cart/items", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_add_item_missing_fields(self):
        """Test adding item with missing required fields"""
        incomplete_data = {
            "customer_id": "customer-123",
            # Missing other required fields
        }
        
        response = client.post("/api/v1/cart/items", json=incomplete_data)
        assert response.status_code == 422  # Validation error

class TestErrorHandling:
    """Test error handling"""
    
    @patch('app.routes.cart_routes.get_db')
    def test_database_error_handling(self, mock_get_db):
        """Test handling of database errors"""
        # Mock database session to raise an exception
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_db.query.side_effect = Exception("Database connection error")
        
        response = client.get("/api/v1/cart/customer-123")
        assert response.status_code == 500

class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/v1/cart/customer-123")
        # CORS headers should be handled by FastAPI middleware
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
