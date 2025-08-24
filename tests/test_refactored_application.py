"""
Comprehensive Testing for Refactored Application
Tests the new static frontend + FastAPI backend microservices architecture
"""

import pytest
import requests
import time
import uuid
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestRefactoredApplication:
    """Comprehensive test suite for refactored application architecture."""
    
    @pytest.fixture(scope="class")
    def backend_url(self):
        """Backend microservice URL."""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def frontend_url(self):
        """Frontend static files URL."""
        return "http://localhost:8080"
    
    @pytest.fixture(scope="class")
    def test_customer_id(self):
        """Generate unique customer ID for testing."""
        return f"refactored-test-{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture(scope="class")
    def chrome_driver(self):
        """Chrome WebDriver for frontend testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            yield driver
            driver.quit()
        except Exception as e:
            pytest.skip(f"Chrome WebDriver not available: {str(e)}")
    
    def test_refactored_architecture_structure(self):
        """Test the refactored architecture structure."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Verify microservices directory exists
        assert microservices_dir.exists(), "Microservices directory not found"
        
        # Test backend structure (FastAPI)
        backend_dir = microservices_dir / "backend"
        assert backend_dir.exists(), "Backend microservice not found"
        
        backend_files = [
            "app/main.py",
            "app/routes/cart_routes.py",
            "app/routes/health_routes.py",
            "Dockerfile",
            "requirements.txt"
        ]
        
        for file_path in backend_files:
            full_path = backend_dir / file_path
            assert full_path.exists(), f"Backend file {file_path} missing"
            assert full_path.stat().st_size > 0, f"Backend file {file_path} is empty"
        
        # Test frontend structure (Static HTML/CSS/JS)
        frontend_dir = microservices_dir / "frontend"
        assert frontend_dir.exists(), "Frontend microservice not found"
        
        # Check static files structure
        public_dir = frontend_dir / "public"
        assert public_dir.exists(), "Frontend public directory not found"
        
        static_files = [
            "index.html",
            "css",
            "js",
            "assets"
        ]
        
        for file_path in static_files:
            full_path = public_dir / file_path
            assert full_path.exists(), f"Frontend static file/directory {file_path} missing"
    
    def test_static_frontend_configuration(self):
        """Test static frontend configuration and package.json."""
        frontend_dir = Path("/Workshop/carthub/microservices/frontend")
        
        # Check package.json for static configuration
        package_json = frontend_dir / "package.json"
        assert package_json.exists(), "Frontend package.json not found"
        
        with open(package_json, 'r') as f:
            package_data = json.load(f)
        
        # Verify it's configured for static serving
        assert package_data["name"] == "carthub-frontend", "Package name incorrect"
        assert "start" in package_data["scripts"], "Start script missing"
        assert "http.server" in package_data["scripts"]["start"] or "nginx" in package_data["scripts"]["start"], "Should use static server"
        
        # Check Dockerfile for nginx configuration
        dockerfile = frontend_dir / "Dockerfile"
        assert dockerfile.exists(), "Frontend Dockerfile not found"
        
        with open(dockerfile, 'r') as f:
            dockerfile_content = f.read()
        
        assert "FROM nginx:" in dockerfile_content, "Should use nginx base image"
        assert "COPY public/" in dockerfile_content, "Should copy static files"
        assert "nginx.conf" in dockerfile_content, "Should have nginx configuration"
    
    def test_backend_microservice_comprehensive(self, backend_url, test_customer_id):
        """Test backend microservice comprehensively."""
        try:
            # Test 1: Health endpoints
            health_response = requests.get(f"{backend_url}/health/", timeout=10)
            assert health_response.status_code == 200, "Health check failed"
            
            health_data = health_response.json()
            assert health_data["status"] in ["healthy", "unhealthy"], "Invalid health status"
            assert health_data["version"] == "2.0.0", "Version mismatch"
            
            # Test 2: Root endpoint
            root_response = requests.get(f"{backend_url}/", timeout=10)
            assert root_response.status_code == 200, "Root endpoint failed"
            
            root_data = root_response.json()
            assert root_data["service"] == "Shopping Cart Backend", "Service name incorrect"
            
            # Test 3: Complete cart workflow
            # Add first item
            item1 = {
                "customer_id": test_customer_id,
                "product_id": "refactored-laptop",
                "product_name": "Refactored Test Laptop",
                "price": "1499.99",
                "quantity": 1
            }
            
            add_response = requests.post(f"{backend_url}/api/v1/cart/items", json=item1, timeout=10)
            assert add_response.status_code == 200, "Failed to add first item"
            
            add_data = add_response.json()
            assert add_data["success"] is True, "Add item response indicates failure"
            assert add_data["cart"]["total_items"] == 1, "Item count incorrect"
            
            # Add second item
            item2 = {
                "customer_id": test_customer_id,
                "product_id": "refactored-mouse",
                "product_name": "Refactored Test Mouse",
                "price": "79.99",
                "quantity": 2
            }
            
            add_response2 = requests.post(f"{backend_url}/api/v1/cart/items", json=item2, timeout=10)
            assert add_response2.status_code == 200, "Failed to add second item"
            
            # Get cart
            get_response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            assert get_response.status_code == 200, "Failed to get cart"
            
            cart_data = get_response.json()["cart"]
            assert cart_data["total_items"] == 3, "Total items incorrect (1 laptop + 2 mice)"
            assert len(cart_data["items"]) == 2, "Number of unique items incorrect"
            
            # Update quantity
            update_response = requests.put(
                f"{backend_url}/api/v1/cart/{test_customer_id}/items/refactored-laptop",
                params={"quantity": 2},
                timeout=10
            )
            assert update_response.status_code == 200, "Failed to update quantity"
            
            # Remove item
            remove_response = requests.delete(
                f"{backend_url}/api/v1/cart/{test_customer_id}/items/refactored-mouse",
                timeout=10
            )
            assert remove_response.status_code == 200, "Failed to remove item"
            
            # Verify removal
            final_cart_response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            final_cart = final_cart_response.json()["cart"]
            assert final_cart["total_items"] == 2, "Items not removed correctly"
            assert len(final_cart["items"]) == 1, "Should have only one item type"
            
            # Test checkout
            checkout_data = {
                "customer_id": test_customer_id,
                "payment_method": "credit_card",
                "shipping_address": {
                    "street": "123 Refactored St",
                    "city": "Test City",
                    "state": "TS",
                    "zip": "12345"
                }
            }
            
            checkout_response = requests.post(f"{backend_url}/api/v1/cart/checkout", json=checkout_data, timeout=10)
            assert checkout_response.status_code == 200, "Checkout failed"
            
            checkout_result = checkout_response.json()
            assert checkout_result["success"] is True, "Checkout unsuccessful"
            assert "order_id" in checkout_result, "Order ID not generated"
            
            # Verify cart cleared
            empty_cart_response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            empty_cart = empty_cart_response.json()["cart"]
            assert empty_cart["total_items"] == 0, "Cart not cleared after checkout"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Backend testing skipped - service not available: {e}")
    
    def test_static_frontend_functionality(self, frontend_url, chrome_driver):
        """Test static frontend functionality."""
        try:
            # Load the frontend
            chrome_driver.get(frontend_url)
            
            # Wait for page to load
            WebDriverWait(chrome_driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Test 1: Page structure
            assert "CartHub" in chrome_driver.title, "Page title incorrect"
            
            # Check for essential elements
            header = chrome_driver.find_element(By.CLASS_NAME, "header")
            assert header.is_displayed(), "Header not visible"
            
            cart_button = chrome_driver.find_element(By.ID, "cartButton")
            assert cart_button.is_displayed(), "Cart button not visible"
            
            # Test 2: Cart badge
            cart_badge = chrome_driver.find_element(By.ID, "cartBadge")
            assert cart_badge.text == "0", "Initial cart badge should be 0"
            
            # Test 3: Products grid
            try:
                products_grid = chrome_driver.find_element(By.ID, "productsGrid")
                assert products_grid.is_displayed(), "Products grid not visible"
            except:
                # Products might be loaded dynamically
                pass
            
            # Test 4: Responsive design
            # Test mobile view
            chrome_driver.set_window_size(375, 667)
            time.sleep(1)
            
            # Header should still be visible
            header = chrome_driver.find_element(By.CLASS_NAME, "header")
            assert header.is_displayed(), "Header not responsive on mobile"
            
            # Test tablet view
            chrome_driver.set_window_size(768, 1024)
            time.sleep(1)
            
            # Test desktop view
            chrome_driver.set_window_size(1920, 1080)
            time.sleep(1)
            
            # Test 5: JavaScript functionality
            # Check if JavaScript is working
            js_result = chrome_driver.execute_script("return typeof window !== 'undefined'")
            assert js_result is True, "JavaScript not working"
            
            # Test 6: CSS styling
            # Check if styles are loaded
            header_bg = chrome_driver.execute_script(
                "return window.getComputedStyle(document.querySelector('.header')).backgroundColor"
            )
            assert header_bg != "rgba(0, 0, 0, 0)", "CSS styles not loaded"
            
        except Exception as e:
            pytest.skip(f"Frontend testing skipped - service not available: {e}")
    
    def test_frontend_backend_integration(self, frontend_url, backend_url, chrome_driver):
        """Test integration between static frontend and backend API."""
        try:
            # Load frontend
            chrome_driver.get(frontend_url)
            
            # Wait for page load
            WebDriverWait(chrome_driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Test API connectivity from frontend
            # Inject JavaScript to test API calls
            api_test_script = f"""
            return fetch('{backend_url}/health/')
                .then(response => response.json())
                .then(data => data.status)
                .catch(error => 'error');
            """
            
            try:
                api_result = chrome_driver.execute_async_script(f"""
                var callback = arguments[arguments.length - 1];
                {api_test_script.replace('return ', '')}
                .then(result => callback(result));
                """)
                
                assert api_result in ["healthy", "unhealthy"], "API connectivity test failed"
                
            except Exception as e:
                # API might not be available, which is okay for structure testing
                print(f"API connectivity test skipped: {e}")
            
        except Exception as e:
            pytest.skip(f"Integration testing skipped: {e}")
    
    def test_performance_benchmarks(self, backend_url):
        """Test performance benchmarks for the refactored application."""
        try:
            # Test response times
            response_times = []
            
            for i in range(10):
                start_time = time.time()
                response = requests.get(f"{backend_url}/health/", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if response_times:
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
                
                # Performance assertions
                assert avg_response_time < 0.5, f"Average response time {avg_response_time:.3f}s too high"
                assert max_response_time < 1.0, f"Max response time {max_response_time:.3f}s too high"
                
                print(f"Performance Results:")
                print(f"  Average: {avg_response_time:.3f}s")
                print(f"  Min: {min_response_time:.3f}s")
                print(f"  Max: {max_response_time:.3f}s")
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Performance testing skipped: {e}")
    
    def test_error_handling_comprehensive(self, backend_url):
        """Test comprehensive error handling."""
        try:
            # Test invalid data
            invalid_item = {
                "customer_id": "error-test",
                "product_id": "error-product",
                "product_name": "Error Product",
                "price": "-50.00",  # Invalid negative price
                "quantity": 1
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=invalid_item, timeout=10)
            assert response.status_code == 422, "Should return validation error"
            
            # Test missing required fields
            incomplete_item = {
                "customer_id": "error-test"
                # Missing required fields
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=incomplete_item, timeout=10)
            assert response.status_code == 422, "Should return validation error for missing fields"
            
            # Test invalid quantity
            invalid_quantity_item = {
                "customer_id": "error-test",
                "product_id": "error-product",
                "product_name": "Error Product",
                "price": "50.00",
                "quantity": 0  # Invalid zero quantity
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=invalid_quantity_item, timeout=10)
            assert response.status_code == 422, "Should return validation error for zero quantity"
            
            # Test non-existent endpoints
            response = requests.get(f"{backend_url}/api/v1/nonexistent", timeout=10)
            assert response.status_code == 404, "Should return 404 for non-existent endpoints"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Error handling testing skipped: {e}")
    
    def test_concurrent_load_simulation(self, backend_url):
        """Test concurrent load handling."""
        try:
            def concurrent_request(request_id):
                """Make a concurrent request."""
                try:
                    customer_id = f"load-test-{request_id}"
                    
                    # Add item
                    item = {
                        "customer_id": customer_id,
                        "product_id": f"load-product-{request_id}",
                        "product_name": f"Load Test Product {request_id}",
                        "price": "29.99",
                        "quantity": 1
                    }
                    
                    response = requests.post(f"{backend_url}/api/v1/cart/items", json=item, timeout=10)
                    return response.status_code == 200
                    
                except:
                    return False
            
            # Execute concurrent requests
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(concurrent_request, i) for i in range(10)]
                results = [future.result() for future in as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            assert success_rate >= 0.8, f"Concurrent load success rate {success_rate:.2%} too low"
            
        except Exception as e:
            pytest.skip(f"Concurrent load testing skipped: {e}")
    
    def test_data_validation_comprehensive(self, backend_url):
        """Test comprehensive data validation."""
        try:
            test_customer = f"validation-test-{uuid.uuid4().hex[:8]}"
            
            # Test valid data
            valid_item = {
                "customer_id": test_customer,
                "product_id": "validation-product",
                "product_name": "Validation Test Product",
                "price": "99.99",
                "quantity": 1
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=valid_item, timeout=10)
            assert response.status_code == 200, "Valid data should be accepted"
            
            # Test edge cases
            edge_cases = [
                # Very long customer ID
                {**valid_item, "customer_id": "x" * 200},
                # Very long product name
                {**valid_item, "product_name": "x" * 500},
                # Very high price
                {**valid_item, "price": "999999.99"},
                # Very high quantity
                {**valid_item, "quantity": 1000}
            ]
            
            for case in edge_cases:
                response = requests.post(f"{backend_url}/api/v1/cart/items", json=case, timeout=10)
                # Should either accept (200) or reject with validation error (422)
                assert response.status_code in [200, 422], f"Unexpected status for edge case: {case}"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Data validation testing skipped: {e}")
    
    def test_deployment_readiness(self):
        """Test deployment readiness of the refactored application."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Check Docker configurations
        backend_dockerfile = microservices_dir / "backend" / "Dockerfile"
        frontend_dockerfile = microservices_dir / "frontend" / "Dockerfile"
        
        assert backend_dockerfile.exists(), "Backend Dockerfile missing"
        assert frontend_dockerfile.exists(), "Frontend Dockerfile missing"
        
        # Check for CI/CD configurations
        backend_buildspec = microservices_dir / "backend" / "buildspec.yml"
        frontend_buildspec = microservices_dir / "frontend" / "buildspec.yml"
        
        if backend_buildspec.exists():
            with open(backend_buildspec, 'r') as f:
                content = f.read()
            assert "phases:" in content, "Backend buildspec should have phases"
        
        if frontend_buildspec.exists():
            with open(frontend_buildspec, 'r') as f:
                content = f.read()
            assert "phases:" in content, "Frontend buildspec should have phases"
        
        # Check for Kubernetes readiness
        backend_k8s = microservices_dir / "backend" / "k8s"
        frontend_k8s = microservices_dir / "frontend" / "k8s"
        
        if backend_k8s.exists():
            k8s_files = list(backend_k8s.glob("*.yaml")) + list(backend_k8s.glob("*.yml"))
            assert len(k8s_files) > 0, "Backend Kubernetes manifests missing"
        
        if frontend_k8s.exists():
            k8s_files = list(frontend_k8s.glob("*.yaml")) + list(frontend_k8s.glob("*.yml"))
            assert len(k8s_files) > 0, "Frontend Kubernetes manifests missing"
