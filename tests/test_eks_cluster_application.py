"""
EKS Cluster Application Testing Suite
Tests the live CartHub application deployed on AWS EKS cluster
"""

import pytest
import requests
import time
import uuid
import subprocess
import json
from pathlib import Path


class TestEKSClusterApplication:
    """Comprehensive test suite for EKS deployed CartHub application."""
    
    @pytest.fixture(scope="class")
    def frontend_url(self):
        """Frontend application URL from EKS ingress."""
        return "http://k8s-shopping-frontend-4268003632-703545603.us-east-1.elb.amazonaws.com"
    
    @pytest.fixture(scope="class")
    def backend_url(self):
        """Backend API URL via port-forward."""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_backend_port_forward(self):
        """Set up port forwarding to backend service."""
        # Start port forwarding
        proc = subprocess.Popen([
            "kubectl", "port-forward", "-n", "shopping-cart", 
            "svc/backend-service", "8000:8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for port forward to be ready
        time.sleep(3)
        
        yield
        
        # Cleanup
        proc.terminate()
        proc.wait()
    
    @pytest.fixture(scope="class")
    def test_customer_id(self):
        """Generate unique customer ID for testing."""
        return f"eks-test-{uuid.uuid4().hex[:8]}"
    
    def test_eks_cluster_connectivity(self):
        """Test EKS cluster connectivity and basic info."""
        # Test kubectl connectivity
        result = subprocess.run(
            ["kubectl", "cluster-info"], 
            capture_output=True, text=True, timeout=10
        )
        
        assert result.returncode == 0, "kubectl cluster-info failed"
        assert "Kubernetes control plane is running" in result.stdout, "EKS cluster not accessible"
        assert "eks.amazonaws.com" in result.stdout, "Not connected to EKS cluster"
    
    def test_shopping_cart_namespace_deployment(self):
        """Test shopping-cart namespace and deployments."""
        # Check namespace exists
        result = subprocess.run(
            ["kubectl", "get", "namespace", "shopping-cart"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "shopping-cart namespace not found"
        
        # Check deployments
        result = subprocess.run(
            ["kubectl", "get", "deployments", "-n", "shopping-cart"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "Failed to get deployments"
        assert "backend-deployment" in result.stdout, "Backend deployment not found"
        assert "frontend-deployment" in result.stdout, "Frontend deployment not found"
        
        # Check all pods are running
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", "shopping-cart"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "Failed to get pods"
        assert "Running" in result.stdout, "No running pods found"
        
        # Verify no failed pods
        lines = result.stdout.split('\n')
        for line in lines[1:]:  # Skip header
            if line.strip() and "pod/" in line:
                assert "Error" not in line, f"Pod in error state: {line}"
                assert "CrashLoopBackOff" not in line, f"Pod crashing: {line}"
    
    def test_frontend_application_live(self, frontend_url):
        """Test live frontend application on EKS."""
        try:
            # Test frontend accessibility
            response = requests.get(frontend_url, timeout=10)
            assert response.status_code == 200, f"Frontend returned {response.status_code}"
            
            # Check content
            content = response.text
            assert "CartHub" in content, "CartHub title not found in frontend"
            assert "Modern Shopping Cart" in content, "Shopping cart content not found"
            assert "cart.css" in content, "CSS reference not found"
            
            # Check for essential HTML structure
            assert "<html" in content, "HTML structure not found"
            assert "<head>" in content, "HTML head not found"
            assert "<body>" in content, "HTML body not found"
            
            print(f"✅ Frontend application accessible at {frontend_url}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Frontend application not accessible: {e}")
    
    def test_backend_api_live(self, backend_url):
        """Test live backend API on EKS."""
        try:
            # Test root endpoint
            response = requests.get(f"{backend_url}/", timeout=10)
            assert response.status_code == 200, f"Backend root returned {response.status_code}"
            
            root_data = response.json()
            assert root_data["service"] == "Shopping Cart Backend", "Service name incorrect"
            assert root_data["version"] == "2.0.0", "Version incorrect"
            assert root_data["status"] == "running", "Service not running"
            
            print(f"✅ Backend API accessible at {backend_url}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Backend API not accessible: {e}")
    
    def test_backend_health_endpoints_live(self, backend_url):
        """Test backend health endpoints on live EKS deployment."""
        try:
            # Test health endpoint
            response = requests.get(f"{backend_url}/health/", timeout=10)
            assert response.status_code == 200, "Health endpoint failed"
            
            health_data = response.json()
            assert "status" in health_data, "Health status missing"
            assert "timestamp" in health_data, "Health timestamp missing"
            assert "version" in health_data, "Health version missing"
            
            print("✅ Health endpoints working on EKS")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Health endpoints not working: {e}")
    
    def test_cart_api_functionality_live(self, backend_url, test_customer_id):
        """Test cart API functionality on live EKS deployment."""
        try:
            # Test 1: Add item to cart
            item_data = {
                "customer_id": test_customer_id,
                "product_id": "eks-test-laptop",
                "product_name": "EKS Test Laptop",
                "price": "1299.99",
                "quantity": 1
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=item_data, timeout=10)
            assert response.status_code == 200, f"Add item failed: {response.status_code}"
            
            add_response = response.json()
            assert add_response["success"] is True, "Add item response indicates failure"
            
            # Test 2: Get cart
            response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            assert response.status_code == 200, "Get cart failed"
            
            cart_response = response.json()
            assert cart_response["success"] is True, "Get cart response indicates failure"
            assert cart_response["cart"]["total_items"] == 1, "Cart item count incorrect"
            
            # Test 3: Update quantity
            response = requests.put(
                f"{backend_url}/api/v1/cart/{test_customer_id}/items/eks-test-laptop",
                params={"quantity": 2},
                timeout=10
            )
            assert response.status_code == 200, "Update quantity failed"
            
            # Test 4: Remove item
            response = requests.delete(
                f"{backend_url}/api/v1/cart/{test_customer_id}/items/eks-test-laptop",
                timeout=10
            )
            assert response.status_code == 200, "Remove item failed"
            
            # Test 5: Verify cart is empty
            response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            final_cart = response.json()["cart"]
            assert final_cart["total_items"] == 0, "Cart not empty after removal"
            
            print("✅ Cart API functionality working on EKS")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Cart API functionality failed: {e}")
    
    def test_checkout_functionality_live(self, backend_url, test_customer_id):
        """Test checkout functionality on live EKS deployment."""
        try:
            # Add item first
            item_data = {
                "customer_id": test_customer_id,
                "product_id": "eks-checkout-item",
                "product_name": "EKS Checkout Test Item",
                "price": "99.99",
                "quantity": 2
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/items", json=item_data, timeout=10)
            assert response.status_code == 200, "Failed to add item for checkout test"
            
            # Test checkout
            checkout_data = {
                "customer_id": test_customer_id,
                "payment_method": "credit_card",
                "shipping_address": {
                    "street": "123 EKS Test St",
                    "city": "Test City",
                    "state": "TS",
                    "zip": "12345"
                }
            }
            
            response = requests.post(f"{backend_url}/api/v1/cart/checkout", json=checkout_data, timeout=10)
            assert response.status_code == 200, "Checkout failed"
            
            checkout_response = response.json()
            assert checkout_response["success"] is True, "Checkout response indicates failure"
            assert "order_id" in checkout_response, "Order ID not generated"
            
            print("✅ Checkout functionality working on EKS")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Checkout functionality failed: {e}")
    
    def test_eks_pod_health_and_logs(self):
        """Test EKS pod health and check logs for errors."""
        # Get pod status
        result = subprocess.run(
            ["kubectl", "get", "pods", "-n", "shopping-cart", "-o", "json"], 
            capture_output=True, text=True, timeout=15
        )
        assert result.returncode == 0, "Failed to get pod status"
        
        pods_data = json.loads(result.stdout)
        
        for pod in pods_data["items"]:
            pod_name = pod["metadata"]["name"]
            
            # Check pod is running
            phase = pod["status"]["phase"]
            assert phase == "Running", f"Pod {pod_name} not running: {phase}"
            
            # Check container status
            if "containerStatuses" in pod["status"]:
                for container in pod["status"]["containerStatuses"]:
                    assert container["ready"] is True, f"Container in {pod_name} not ready"
                    assert container["state"].get("running") is not None, f"Container in {pod_name} not running"
            
            # Check recent logs for errors (last 50 lines)
            log_result = subprocess.run(
                ["kubectl", "logs", "-n", "shopping-cart", pod_name, "--tail=50"], 
                capture_output=True, text=True, timeout=10
            )
            
            if log_result.returncode == 0:
                logs = log_result.stdout.lower()
                # Check for critical errors (but allow INFO/DEBUG logs)
                critical_errors = ["fatal", "panic", "crash", "exception", "traceback"]
                for error in critical_errors:
                    assert error not in logs, f"Critical error '{error}' found in {pod_name} logs"
        
        print("✅ All pods healthy with no critical errors in logs")
    
    def test_eks_service_connectivity(self):
        """Test EKS service connectivity and endpoints."""
        # Test backend service
        result = subprocess.run(
            ["kubectl", "get", "endpoints", "-n", "shopping-cart", "backend-service"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "Backend service endpoints not found"
        assert "8000" in result.stdout, "Backend service port not configured"
        
        # Test frontend service
        result = subprocess.run(
            ["kubectl", "get", "endpoints", "-n", "shopping-cart", "frontend-service"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "Frontend service endpoints not found"
        assert "80" in result.stdout, "Frontend service port not configured"
        
        print("✅ EKS services have proper endpoints")
    
    def test_eks_ingress_configuration(self):
        """Test EKS ingress configuration and load balancer."""
        # Check ingress exists
        result = subprocess.run(
            ["kubectl", "get", "ingress", "-n", "shopping-cart", "frontend-ingress"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "Frontend ingress not found"
        assert "elb.amazonaws.com" in result.stdout, "AWS Load Balancer not configured"
        
        # Check ingress has address
        result = subprocess.run(
            ["kubectl", "get", "ingress", "-n", "shopping-cart", "frontend-ingress", "-o", "json"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "Failed to get ingress details"
        
        ingress_data = json.loads(result.stdout)
        if "status" in ingress_data and "loadBalancer" in ingress_data["status"]:
            ingress_list = ingress_data["status"]["loadBalancer"].get("ingress", [])
            assert len(ingress_list) > 0, "Ingress has no load balancer address"
        
        print("✅ EKS ingress properly configured with AWS Load Balancer")
    
    def test_eks_resource_utilization(self):
        """Test EKS resource utilization and limits."""
        # Check pod resource usage
        result = subprocess.run(
            ["kubectl", "top", "pods", "-n", "shopping-cart"], 
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode == 0:
            # If metrics are available, check they're reasonable
            lines = result.stdout.split('\n')
            for line in lines[1:]:  # Skip header
                if line.strip() and "deployment" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        cpu = parts[1]
                        memory = parts[2]
                        
                        # Basic sanity checks (not too high)
                        if "m" in cpu:  # millicores
                            cpu_val = int(cpu.replace('m', ''))
                            assert cpu_val < 2000, f"CPU usage too high: {cpu}"
                        
                        if "Mi" in memory:  # Megabytes
                            mem_val = int(memory.replace('Mi', ''))
                            assert mem_val < 1000, f"Memory usage too high: {memory}"
            
            print("✅ EKS resource utilization within reasonable limits")
        else:
            print("⚠️ Metrics server not available, skipping resource utilization check")
    
    def test_eks_application_scalability(self):
        """Test EKS application scalability features."""
        # Check current replica count
        result = subprocess.run(
            ["kubectl", "get", "deployments", "-n", "shopping-cart", "-o", "json"], 
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, "Failed to get deployment info"
        
        deployments = json.loads(result.stdout)
        
        for deployment in deployments["items"]:
            name = deployment["metadata"]["name"]
            replicas = deployment["spec"]["replicas"]
            ready_replicas = deployment["status"].get("readyReplicas", 0)
            
            # Check all replicas are ready
            assert ready_replicas == replicas, f"Deployment {name}: {ready_replicas}/{replicas} replicas ready"
            
            # Check deployment has reasonable replica count (at least 1, not too many)
            assert 1 <= replicas <= 10, f"Deployment {name} has unusual replica count: {replicas}"
        
        print("✅ EKS deployments properly scaled and ready")
    
    def test_eks_application_end_to_end(self, frontend_url, backend_url, test_customer_id):
        """Test complete end-to-end application workflow on EKS."""
        try:
            # Step 1: Verify frontend is accessible
            frontend_response = requests.get(frontend_url, timeout=10)
            assert frontend_response.status_code == 200, "Frontend not accessible"
            
            # Step 2: Verify backend API is working
            backend_response = requests.get(f"{backend_url}/", timeout=10)
            assert backend_response.status_code == 200, "Backend not accessible"
            
            # Step 3: Complete shopping workflow
            # Add item
            item = {
                "customer_id": test_customer_id,
                "product_id": "e2e-test-product",
                "product_name": "End-to-End Test Product",
                "price": "199.99",
                "quantity": 3
            }
            
            add_response = requests.post(f"{backend_url}/api/v1/cart/items", json=item, timeout=10)
            assert add_response.status_code == 200, "Failed to add item in E2E test"
            
            # Get cart
            cart_response = requests.get(f"{backend_url}/api/v1/cart/{test_customer_id}", timeout=10)
            assert cart_response.status_code == 200, "Failed to get cart in E2E test"
            
            cart_data = cart_response.json()["cart"]
            assert cart_data["total_items"] == 3, "Cart items incorrect in E2E test"
            
            # Checkout
            checkout_data = {
                "customer_id": test_customer_id,
                "payment_method": "credit_card",
                "shipping_address": {"street": "123 E2E St", "city": "Test", "state": "TS", "zip": "12345"}
            }
            
            checkout_response = requests.post(f"{backend_url}/api/v1/cart/checkout", json=checkout_data, timeout=10)
            assert checkout_response.status_code == 200, "Checkout failed in E2E test"
            
            checkout_result = checkout_response.json()
            assert checkout_result["success"] is True, "Checkout unsuccessful in E2E test"
            assert "order_id" in checkout_result, "Order ID not generated in E2E test"
            
            print("✅ Complete end-to-end workflow successful on EKS")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"End-to-end test failed: {e}")
    
    def test_eks_application_performance(self, backend_url):
        """Test EKS application performance characteristics."""
        try:
            response_times = []
            
            # Test multiple requests to measure performance
            for i in range(5):
                start_time = time.time()
                response = requests.get(f"{backend_url}/health/", timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                
                # Performance assertions for EKS deployment
                assert avg_response_time < 2.0, f"Average response time too high: {avg_response_time:.3f}s"
                assert max_response_time < 5.0, f"Max response time too high: {max_response_time:.3f}s"
                
                print(f"✅ EKS application performance: avg={avg_response_time:.3f}s, max={max_response_time:.3f}s")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Performance test failed: {e}")
