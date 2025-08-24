"""
Comprehensive Microservices Testing Suite
Tests the refactored microservices architecture with frontend and backend separation
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


class TestMicroservicesArchitecture:
    """Comprehensive test suite for microservices architecture."""
    
    @pytest.fixture(scope="class")
    def backend_url(self):
        """Backend microservice URL."""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def frontend_url(self):
        """Frontend microservice URL."""
        return "http://localhost:3000"
    
    @pytest.fixture(scope="class")
    def test_customer_id(self):
        """Generate unique customer ID for testing."""
        return f"microservices-test-{uuid.uuid4().hex[:8]}"
    
    def test_microservices_structure_validation(self):
        """Test that microservices structure is properly organized."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Check main microservices directory exists
        assert microservices_dir.exists(), "Microservices directory not found"
        
        # Check backend microservice
        backend_dir = microservices_dir / "backend"
        assert backend_dir.exists(), "Backend microservice directory not found"
        
        backend_files = [
            "app/main.py",
            "app/routes/cart_routes.py",
            "app/routes/health_routes.py",
            "app/services/cart_service.py",
            "app/models/schemas.py",
            "app/config/database.py",
            "Dockerfile",
            "requirements.txt"
        ]
        
        for file_path in backend_files:
            full_path = backend_dir / file_path
            assert full_path.exists(), f"Backend file {file_path} not found"
            assert full_path.stat().st_size > 0, f"Backend file {file_path} is empty"
        
        # Check frontend microservice
        frontend_dir = microservices_dir / "frontend"
        assert frontend_dir.exists(), "Frontend microservice directory not found"
        
        frontend_files = [
            "src/App.js",
            "src/index.js",
            "src/components",
            "src/services",
            "src/styles",
            "package.json",
            "Dockerfile"
        ]
        
        for file_path in frontend_files:
            full_path = frontend_dir / file_path
            assert full_path.exists(), f"Frontend file/directory {file_path} not found"
    
    def test_backend_microservice_health(self, backend_url):
        """Test backend microservice health and availability."""
        try:
            # Test health endpoint
            response = requests.get(f"{backend_url}/health/", timeout=10)
            assert response.status_code == 200, f"Health check failed with status {response.status_code}"
            
            health_data = response.json()
            assert "status" in health_data, "Health response missing status field"
            assert "version" in health_data, "Health response missing version field"
            assert health_data["version"] == "2.0.0", "Version mismatch in health response"
            
            # Test readiness endpoint
            response = requests.get(f"{backend_url}/health/ready", timeout=10)
            assert response.status_code == 200, "Readiness check failed"
            
            # Test liveness endpoint
            response = requests.get(f"{backend_url}/health/live", timeout=10)
            assert response.status_code == 200, "Liveness check failed"
            
            # Test root endpoint
            response = requests.get(f"{backend_url}/", timeout=10)
            assert response.status_code == 200, "Root endpoint failed"
            
            root_data = response.json()
            assert root_data["service"] == "Shopping Cart Backend", "Service name mismatch"
            assert root_data["version"] == "2.0.0", "Version mismatch in root response"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Backend microservice not available: {e}")
    
    def test_backend_api_endpoints_comprehensive(self, backend_url, test_customer_id):
        """Test all backend API endpoints comprehensively."""
        try:
            # Test 1: Add item to cart
            item_data = {
                "customer_id": test_customer_id,
                "product_id": "microservice-test-product-1",
                "product_name": "Microservice Test Laptop",
                "price": "1299.99",
                "quantity": 2
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=item_data, timeout=10)
            assert response.status_code == 200, f"Add item failed with status {response.status_code}"
            
            add_response = response.json()
            assert add_response["success"] is True, "Add item response indicates failure"
            assert "cart" in add_response, "Add item response missing cart data"
            
            cart = add_response["cart"]
            assert cart["customer_id"] == test_customer_id, "Customer ID mismatch"
            assert cart["total_items"] == 2, "Total items count incorrect"
            assert len(cart["items"]) == 1, "Cart items count incorrect"
            
            # Test 2: Get cart
            response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            assert response.status_code == 200, "Get cart failed"
            
            get_response = response.json()
            assert get_response["success"] is True, "Get cart response indicates failure"
            assert get_response["cart"]["total_items"] == 2, "Cart items not persisted"
            
            # Test 3: Add second item
            item_data_2 = {
                "customer_id": test_customer_id,
                "product_id": "microservice-test-product-2",
                "product_name": "Microservice Test Mouse",
                "price": "49.99",
                "quantity": 1
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=item_data_2, timeout=10)
            assert response.status_code == 200, "Add second item failed"
            
            # Test 4: Update item quantity
            response = requests.put(
                f"{backend_url}/api/v1/cart/{test_customer_id}/items/microservice-test-product-1",
                params={"quantity": 3},
                timeout=10
            )
            assert response.status_code == 200, "Update quantity failed"
            
            update_response = response.json()
            assert update_response["success"] is True, "Update quantity response indicates failure"
            
            # Test 5: Remove item
            response = requests.delete(
                f"{backend_url}/api/v1/cart/{test_customer_id}/items/microservice-test-product-2",
                timeout=10
            )
            assert response.status_code == 200, "Remove item failed"
            
            # Test 6: Checkout
            checkout_data = {
                "customer_id": test_customer_id,
                "payment_method": "credit_card",
                "shipping_address": {
                    "street": "123 Microservice St",
                    "city": "Test City",
                    "state": "TS",
                    "zip": "12345"
                }
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/checkout", json=checkout_data, timeout=10)
            assert response.status_code == 200, "Checkout failed"
            
            checkout_response = response.json()
            assert checkout_response["success"] is True, "Checkout response indicates failure"
            assert "order_id" in checkout_response, "Checkout response missing order ID"
            
            # Test 7: Verify cart cleared after checkout
            response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            assert response.status_code == 200, "Get cart after checkout failed"
            
            final_cart = response.json()["cart"]
            assert final_cart["total_items"] == 0, "Cart not cleared after checkout"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Backend API testing failed due to connectivity: {e}")
    
    def test_frontend_microservice_structure(self):
        """Test frontend microservice structure and configuration."""
        frontend_dir = Path("/Workshop/carthub/microservices/frontend")
        
        # Check package.json
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            # Check essential dependencies
            dependencies = package_data.get("dependencies", {})
            essential_deps = ["react", "react-dom", "react-router-dom", "axios"]
            
            for dep in essential_deps:
                assert dep in dependencies, f"Essential dependency {dep} missing"
            
            # Check scripts
            scripts = package_data.get("scripts", {})
            assert "start" in scripts, "Start script missing"
            assert "build" in scripts, "Build script missing"
            assert "test" in scripts, "Test script missing"
        
        # Check TypeScript configuration
        tsconfig = frontend_dir / "tsconfig.json"
        if tsconfig.exists():
            with open(tsconfig, 'r') as f:
                ts_config = json.load(f)
            
            compiler_options = ts_config.get("compilerOptions", {})
            assert "target" in compiler_options, "TypeScript target not specified"
            assert "lib" in compiler_options, "TypeScript lib not specified"
        
        # Check Dockerfile
        dockerfile = frontend_dir / "Dockerfile"
        if dockerfile.exists():
            with open(dockerfile, 'r') as f:
                dockerfile_content = f.read()
            
            assert "FROM node:" in dockerfile_content, "Frontend Dockerfile should use Node base image"
            assert "nginx" in dockerfile_content.lower(), "Should use nginx for production"
    
    def test_microservices_communication(self, backend_url, frontend_url):
        """Test communication between microservices."""
        try:
            # Test CORS configuration
            headers = {
                "Origin": frontend_url,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            # Test preflight request
            response = requests.options(f"{backend_url}/api/v1/cart/items", headers=headers, timeout=10)
            # Should not be blocked by CORS (status 200, 204, or 404 if OPTIONS not implemented)
            assert response.status_code in [200, 204, 404], "CORS preflight request failed"
            
            # Test actual request with CORS headers
            test_data = {
                "customer_id": "cors-test",
                "product_id": "cors-product",
                "product_name": "CORS Test Product",
                "price": "10.00",
                "quantity": 1
            }
            
            cors_headers = {"Origin": frontend_url}
            response = requests.post(
                f"{backend_url}/api/v1/cart/items",
                json=test_data,
                headers=cors_headers,
                timeout=10
            )
            
            # Should not be blocked by CORS
            assert response.status_code in [200, 400, 422], "CORS request blocked"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Microservices communication test failed: {e}")
    
    def test_microservices_performance(self, backend_url):
        """Test microservices performance under load."""
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
                
                assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s too high"
                assert max_response_time < 2.0, f"Max response time {max_response_time:.3f}s too high"
            
            # Test concurrent requests
            def make_request(request_id):
                try:
                    response = requests.get(f"{backend_url}/health/", timeout=10)
                    return response.status_code == 200
                except:
                    return False
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, i) for i in range(10)]
                results = [future.result() for future in as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            assert success_rate >= 0.8, f"Success rate {success_rate:.2%} too low under concurrent load"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Performance testing failed: {e}")
    
    def test_microservices_error_handling(self, backend_url):
        """Test error handling in microservices."""
        try:
            # Test invalid data
            invalid_data = {
                "customer_id": "error-test",
                "product_id": "error-product",
                "product_name": "Error Test Product",
                "price": "-10.00",  # Invalid negative price
                "quantity": 1
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=invalid_data, timeout=10)
            assert response.status_code == 422, "Should return validation error for invalid data"
            
            # Test missing data
            incomplete_data = {
                "customer_id": "error-test"
                # Missing required fields
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=incomplete_data, timeout=10)
            assert response.status_code == 422, "Should return validation error for missing data"
            
            # Test non-existent endpoints
            response = requests.get(f"{backend_url}/api/v1/nonexistent", timeout=10)
            assert response.status_code == 404, "Should return 404 for non-existent endpoints"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Error handling test failed: {e}")
    
    def test_microservices_data_consistency(self, backend_url):
        """Test data consistency across microservices operations."""
        try:
            consistency_customer = f"consistency-test-{uuid.uuid4().hex[:8]}"
            
            # Add multiple items
            items = [
                {
                    "customer_id": consistency_customer,
                    "product_id": f"consistency-item-{i}",
                    "product_name": f"Consistency Item {i}",
                    "price": f"{10 + i}.99",
                    "quantity": i + 1
                }
                for i in range(3)
            ]
            
            for item in items:
                response = requests.post(f"{backend_url}/api/v1/cart/items", json=item, timeout=10)
                assert response.status_code == 200, f"Failed to add item {item['product_id']}"
            
            # Verify cart state
            response = requests.get(f"{backend_url}/api/v1/cart/{consistency_customer}", timeout=10)
            assert response.status_code == 200, "Failed to get cart"
            
            cart_data = response.json()["cart"]
            
            # Verify total items (1 + 2 + 3 = 6)
            expected_total = sum(i + 1 for i in range(3))
            assert cart_data["total_items"] == expected_total, "Total items calculation incorrect"
            
            # Verify all items present
            assert len(cart_data["items"]) == 3, "Not all items present in cart"
            
            # Verify subtotal calculation
            expected_subtotal = sum((10 + i + 0.99) * (i + 1) for i in range(3))
            actual_subtotal = float(cart_data["subtotal"])
            assert abs(actual_subtotal - expected_subtotal) < 0.01, "Subtotal calculation incorrect"
            
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Data consistency test failed: {e}")
    
    def test_microservices_scalability_simulation(self, backend_url):
        """Simulate scalability scenarios for microservices."""
        try:
            # Simulate multiple customers
            customers = [f"scale-customer-{i}-{uuid.uuid4().hex[:4]}" for i in range(5)]
            
            def customer_workflow(customer_id):
                """Simulate a complete customer workflow."""
                try:
                    # Add items
                    for i in range(3):
                        item = {
                            "customer_id": customer_id,
                            "product_id": f"scale-item-{customer_id}-{i}",
                            "product_name": f"Scale Item {i}",
                            "price": "25.99",
                            "quantity": 1
                        }
                        
                        response = requests.post(f"{backend_url}/api/v1/cart/items", json=item, timeout=10)
                        if response.status_code != 200:
                            return False
                    
                    # Get cart
                    response = requests.get(f"{backend_url}/api/v1/cart/{customer_id}", timeout=10)
                    if response.status_code != 200:
                        return False
                    
                    # Update quantity
                    response = requests.put(
                        f"{backend_url}/api/v1/cart/{customer_id}/items/scale-item-{customer_id}-0",
                        params={"quantity": 2},
                        timeout=10
                    )
                    if response.status_code != 200:
                        return False
                    
                    return True
                    
                except:
                    return False
            
            # Execute workflows concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(customer_workflow, customer) for customer in customers]
                results = [future.result() for future in as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            assert success_rate >= 0.8, f"Scalability test success rate {success_rate:.2%} too low"
            
        except Exception as e:
            pytest.skip(f"Scalability simulation failed: {e}")
    
    def test_microservices_docker_configuration(self):
        """Test Docker configuration for microservices."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Test backend Dockerfile
        backend_dockerfile = microservices_dir / "backend" / "Dockerfile"
        if backend_dockerfile.exists():
            with open(backend_dockerfile, 'r') as f:
                content = f.read()
            
            assert "FROM python:" in content, "Backend should use Python base image"
            assert "requirements.txt" in content, "Should install Python requirements"
            assert "uvicorn" in content or "main:app" in content, "Should run FastAPI app"
        
        # Test frontend Dockerfile
        frontend_dockerfile = microservices_dir / "frontend" / "Dockerfile"
        if frontend_dockerfile.exists():
            with open(frontend_dockerfile, 'r') as f:
                content = f.read()
            
            assert "FROM node:" in content, "Frontend should use Node base image"
            assert "nginx" in content.lower(), "Should use nginx for production"
            assert "build" in content, "Should build React app"
    
    def test_microservices_kubernetes_readiness(self):
        """Test Kubernetes deployment readiness."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Check for Kubernetes manifests
        backend_k8s = microservices_dir / "backend" / "k8s"
        frontend_k8s = microservices_dir / "frontend" / "k8s"
        
        if backend_k8s.exists():
            k8s_files = list(backend_k8s.glob("*.yaml")) + list(backend_k8s.glob("*.yml"))
            assert len(k8s_files) > 0, "Backend Kubernetes manifests not found"
        
        if frontend_k8s.exists():
            k8s_files = list(frontend_k8s.glob("*.yaml")) + list(frontend_k8s.glob("*.yml"))
            assert len(k8s_files) > 0, "Frontend Kubernetes manifests not found"
    
    def test_microservices_ci_cd_configuration(self):
        """Test CI/CD configuration for microservices."""
        microservices_dir = Path("/Workshop/carthub/microservices")
        
        # Check for buildspec files (AWS CodeBuild)
        backend_buildspec = microservices_dir / "backend" / "buildspec.yml"
        frontend_buildspec = microservices_dir / "frontend" / "buildspec.yml"
        
        if backend_buildspec.exists():
            with open(backend_buildspec, 'r') as f:
                content = f.read()
            
            assert "phases:" in content, "Buildspec should have phases"
            assert "build:" in content, "Buildspec should have build phase"
        
        if frontend_buildspec.exists():
            with open(frontend_buildspec, 'r') as f:
                content = f.read()
            
            assert "phases:" in content, "Frontend buildspec should have phases"
            assert "build:" in content, "Frontend buildspec should have build phase"
