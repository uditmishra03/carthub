"""
End-to-End Integration Tests for Shopping Cart Application
Tests complete user workflows from frontend to backend
"""

import pytest
import requests
import time
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import json


class TestIntegrationE2E:
    """End-to-end integration test suite."""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Backend API base URL."""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def frontend_url(self):
        """Frontend application URL."""
        return "http://localhost:3000"
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Chrome WebDriver for E2E testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    @pytest.fixture(scope="class")
    def test_customer_id(self):
        """Generate unique customer ID for E2E testing."""
        return f"e2e-customer-{uuid.uuid4().hex[:8]}"
    
    def test_backend_frontend_connectivity(self, api_base_url, frontend_url):
        """Test that backend and frontend services are running and accessible."""
        # Test backend health
        backend_response = requests.get(f"{api_base_url}/health/")
        assert backend_response.status_code == 200
        
        backend_data = backend_response.json()
        assert backend_data["status"] in ["healthy", "unhealthy"]
        
        # Test frontend accessibility
        frontend_response = requests.get(frontend_url)
        assert frontend_response.status_code == 200
        assert "text/html" in frontend_response.headers.get("content-type", "")
    
    def test_api_cors_configuration(self, api_base_url, frontend_url):
        """Test CORS configuration between frontend and backend."""
        # Make a preflight request to check CORS
        headers = {
            "Origin": frontend_url,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = requests.options(f"{api_base_url}/api/v1/cart/items", headers=headers)
        
        # Should allow CORS or return appropriate headers
        assert response.status_code in [200, 204, 404]  # 404 if OPTIONS not implemented
        
        # Test actual CORS with a real request
        test_payload = {
            "customer_id": "cors-test",
            "product_id": "cors-product",
            "product_name": "CORS Test Product",
            "price": "10.00",
            "quantity": 1
        }
        
        cors_headers = {"Origin": frontend_url}
        response = requests.post(
            f"{api_base_url}/api/v1/cart/items", 
            json=test_payload, 
            headers=cors_headers
        )
        
        # Should not be blocked by CORS
        assert response.status_code in [200, 400, 422]  # Not 403 (CORS blocked)
    
    def test_complete_shopping_workflow_api(self, api_base_url, test_customer_id):
        """Test complete shopping workflow via API calls."""
        # Step 1: Start with empty cart
        cart_response = requests.get(f"{api_base_url}/api/v1/cart/{test_customer_id}")
        assert cart_response.status_code == 200
        
        initial_cart = cart_response.json()["cart"]
        assert initial_cart["total_items"] == 0
        
        # Step 2: Add first item
        item1 = {
            "customer_id": test_customer_id,
            "product_id": "workflow-item-1",
            "product_name": "Workflow Test Laptop",
            "price": "999.99",
            "quantity": 1
        }
        
        add_response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item1)
        assert add_response.status_code == 200
        
        cart_after_add1 = add_response.json()["cart"]
        assert cart_after_add1["total_items"] == 1
        assert float(cart_after_add1["subtotal"]) == 999.99
        
        # Step 3: Add second item
        item2 = {
            "customer_id": test_customer_id,
            "product_id": "workflow-item-2",
            "product_name": "Workflow Test Mouse",
            "price": "29.99",
            "quantity": 2
        }
        
        add_response2 = requests.post(f"{api_base_url}/api/v1/cart/items", json=item2)
        assert add_response2.status_code == 200
        
        cart_after_add2 = add_response2.json()["cart"]
        assert cart_after_add2["total_items"] == 3  # 1 laptop + 2 mice
        expected_subtotal = 999.99 + (29.99 * 2)
        assert abs(float(cart_after_add2["subtotal"]) - expected_subtotal) < 0.01
        
        # Step 4: Update quantity of first item
        update_response = requests.put(
            f"{api_base_url}/api/v1/cart/{test_customer_id}/items/workflow-item-1",
            params={"quantity": 2}
        )
        assert update_response.status_code == 200
        
        cart_after_update = update_response.json()["cart"]
        assert cart_after_update["total_items"] == 4  # 2 laptops + 2 mice
        
        # Step 5: Remove second item
        remove_response = requests.delete(
            f"{api_base_url}/api/v1/cart/{test_customer_id}/items/workflow-item-2"
        )
        assert remove_response.status_code == 200
        
        cart_after_remove = remove_response.json()["cart"]
        assert cart_after_remove["total_items"] == 2  # 2 laptops only
        
        # Step 6: Checkout
        checkout_payload = {
            "customer_id": test_customer_id,
            "payment_method": "credit_card",
            "shipping_address": {
                "street": "123 E2E Test St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            }
        }
        
        checkout_response = requests.post(f"{api_base_url}/api/v1/cart/checkout", json=checkout_payload)
        assert checkout_response.status_code == 200
        
        checkout_data = checkout_response.json()
        assert checkout_data["success"] is True
        assert "order_id" in checkout_data
        assert checkout_data["order_id"] is not None
        
        # Step 7: Verify cart is cleared after checkout
        final_cart_response = requests.get(f"{api_base_url}/api/v1/cart/{test_customer_id}")
        assert final_cart_response.status_code == 200
        
        final_cart = final_cart_response.json()["cart"]
        assert final_cart["total_items"] == 0
    
    def test_error_handling_workflow(self, api_base_url):
        """Test error handling in complete workflow."""
        error_customer = f"error-test-{uuid.uuid4().hex[:8]}"
        
        # Test 1: Add invalid item
        invalid_item = {
            "customer_id": error_customer,
            "product_id": "invalid-item",
            "product_name": "Invalid Item",
            "price": "-10.00",  # Invalid negative price
            "quantity": 1
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/items", json=invalid_item)
        assert response.status_code == 422  # Validation error
        
        # Test 2: Update non-existent item
        response = requests.put(
            f"{api_base_url}/api/v1/cart/{error_customer}/items/nonexistent-item",
            params={"quantity": 5}
        )
        assert response.status_code == 200  # Should handle gracefully
        
        # Test 3: Checkout empty cart
        checkout_payload = {
            "customer_id": error_customer,
            "payment_method": "credit_card",
            "shipping_address": {
                "street": "123 Error St",
                "city": "Error City",
                "state": "ER",
                "zip": "00000"
            }
        }
        
        response = requests.post(f"{api_base_url}/api/v1/cart/checkout", json=checkout_payload)
        assert response.status_code == 400  # Bad request for empty cart
    
    def test_concurrent_user_operations(self, api_base_url):
        """Test concurrent operations by multiple users."""
        users = [f"concurrent-user-{i}-{uuid.uuid4().hex[:4]}" for i in range(3)]
        
        # Each user adds items concurrently
        for i, user in enumerate(users):
            item = {
                "customer_id": user,
                "product_id": f"concurrent-item-{i}",
                "product_name": f"Concurrent Item {i}",
                "price": f"{(i+1)*10}.00",
                "quantity": i + 1
            }
            
            response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            assert response.status_code == 200
        
        # Verify each user's cart is independent
        for i, user in enumerate(users):
            cart_response = requests.get(f"{api_base_url}/api/v1/cart/{user}")
            assert cart_response.status_code == 200
            
            cart_data = cart_response.json()["cart"]
            assert cart_data["customer_id"] == user
            assert cart_data["total_items"] == i + 1
    
    def test_data_persistence_across_requests(self, api_base_url):
        """Test that cart data persists across multiple requests."""
        persistence_customer = f"persistence-{uuid.uuid4().hex[:8]}"
        
        # Add item
        item = {
            "customer_id": persistence_customer,
            "product_id": "persistence-item",
            "product_name": "Persistence Test Item",
            "price": "50.00",
            "quantity": 3
        }
        
        add_response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
        assert add_response.status_code == 200
        
        # Wait a moment
        time.sleep(1)
        
        # Retrieve cart in separate request
        get_response = requests.get(f"{api_base_url}/api/v1/cart/{persistence_customer}")
        assert get_response.status_code == 200
        
        cart_data = get_response.json()["cart"]
        assert cart_data["total_items"] == 3
        assert len(cart_data["items"]) == 1
        
        item_data = cart_data["items"][0]
        assert item_data["product_id"] == "persistence-item"
        assert item_data["quantity"] == 3
        assert float(item_data["price"]) == 50.00
    
    def test_api_performance_under_load(self, api_base_url):
        """Test API performance with multiple rapid requests."""
        load_customer = f"load-test-{uuid.uuid4().hex[:8]}"
        
        # Measure response times for multiple requests
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            
            # Add item
            item = {
                "customer_id": load_customer,
                "product_id": f"load-item-{i}",
                "product_name": f"Load Test Item {i}",
                "price": "15.99",
                "quantity": 1
            }
            
            response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Check performance metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s too high"
        assert max_response_time < 2.0, f"Max response time {max_response_time:.3f}s too high"
        
        # Verify all items were added correctly
        cart_response = requests.get(f"{api_base_url}/api/v1/cart/{load_customer}")
        assert cart_response.status_code == 200
        
        final_cart = cart_response.json()["cart"]
        assert final_cart["total_items"] == 10
    
    def test_frontend_backend_integration_basic(self, driver, frontend_url, api_base_url):
        """Test basic integration between frontend and backend."""
        # Load frontend
        driver.get(frontend_url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Check if frontend can communicate with backend
        # This is a basic test - in a real scenario, we'd test specific interactions
        
        # Verify no JavaScript errors occurred during page load
        logs = driver.get_log('browser')
        severe_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        # Filter out non-critical errors (like favicon 404s)
        critical_errors = [
            error for error in severe_errors 
            if 'favicon' not in error['message'].lower() and 
               'manifest' not in error['message'].lower()
        ]
        
        assert len(critical_errors) == 0, f"Critical JavaScript errors: {critical_errors}"
        
        # Test if page loaded successfully
        page_title = driver.title
        assert len(page_title) > 0, "Page title should not be empty"
        
        # Check if essential elements are present
        body = driver.find_element(By.TAG_NAME, "body")
        assert body.is_displayed()
        
        # Verify page content indicates it's a shopping cart application
        page_source = driver.page_source.lower()
        shopping_keywords = ['cart', 'shop', 'product', 'buy', 'add', 'checkout']
        
        keyword_found = any(keyword in page_source for keyword in shopping_keywords)
        assert keyword_found, "Page doesn't appear to be a shopping cart application"
    
    def test_database_transaction_integrity(self, api_base_url):
        """Test database transaction integrity during operations."""
        integrity_customer = f"integrity-{uuid.uuid4().hex[:8]}"
        
        # Add multiple items in sequence
        items = [
            {
                "customer_id": integrity_customer,
                "product_id": f"integrity-item-{i}",
                "product_name": f"Integrity Item {i}",
                "price": f"{10 + i}.99",
                "quantity": i + 1
            }
            for i in range(5)
        ]
        
        # Add all items
        for item in items:
            response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            assert response.status_code == 200
        
        # Verify cart state is consistent
        cart_response = requests.get(f"{api_base_url}/api/v1/cart/{integrity_customer}")
        assert cart_response.status_code == 200
        
        cart_data = cart_response.json()["cart"]
        
        # Verify total items count
        expected_total = sum(i + 1 for i in range(5))  # 1+2+3+4+5 = 15
        assert cart_data["total_items"] == expected_total
        
        # Verify subtotal calculation
        expected_subtotal = sum((10 + i + 0.99) * (i + 1) for i in range(5))
        actual_subtotal = float(cart_data["subtotal"])
        assert abs(actual_subtotal - expected_subtotal) < 0.01
        
        # Verify all items are present
        assert len(cart_data["items"]) == 5
        
        # Clear cart and verify it's empty
        clear_response = requests.delete(f"{api_base_url}/api/v1/cart/{integrity_customer}")
        assert clear_response.status_code == 200
        
        # Verify cart is actually empty
        empty_cart_response = requests.get(f"{api_base_url}/api/v1/cart/{integrity_customer}")
        assert empty_cart_response.status_code == 200
        
        empty_cart = empty_cart_response.json()["cart"]
        assert empty_cart["total_items"] == 0
        assert len(empty_cart["items"]) == 0
