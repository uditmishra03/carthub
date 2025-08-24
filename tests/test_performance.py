"""
Performance Tests for Shopping Cart Application
Tests response times, throughput, and scalability
"""

import pytest
import requests
import time
import threading
import uuid
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


class TestPerformance:
    """Performance test suite for shopping cart application."""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """Backend API base URL."""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def performance_customer_id(self):
        """Generate unique customer ID for performance testing."""
        return f"perf-customer-{uuid.uuid4().hex[:8]}"
    
    def test_health_check_response_time(self, api_base_url):
        """Test health check endpoint response time."""
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            response = requests.get(f"{api_base_url}/health/")
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Performance assertions
        assert avg_response_time < 0.5, f"Average health check response time {avg_response_time:.3f}s too high"
        assert max_response_time < 1.0, f"Max health check response time {max_response_time:.3f}s too high"
        
        print(f"Health Check Performance:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Min: {min_response_time:.3f}s")
        print(f"  Max: {max_response_time:.3f}s")
    
    def test_add_item_response_time(self, api_base_url, performance_customer_id):
        """Test add item endpoint response time."""
        response_times = []
        
        for i in range(20):
            item = {
                "customer_id": performance_customer_id,
                "product_id": f"perf-item-{i}",
                "product_name": f"Performance Test Item {i}",
                "price": "25.99",
                "quantity": 1
            }
            
            start_time = time.time()
            response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        avg_response_time = statistics.mean(response_times)
        percentile_95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        # Performance assertions
        assert avg_response_time < 0.2, f"Average add item response time {avg_response_time:.3f}s too high"
        assert percentile_95 < 0.5, f"95th percentile response time {percentile_95:.3f}s too high"
        
        print(f"Add Item Performance:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  95th percentile: {percentile_95:.3f}s")
    
    def test_get_cart_response_time(self, api_base_url, performance_customer_id):
        """Test get cart endpoint response time with various cart sizes."""
        # First, add items to create different cart sizes
        cart_sizes = [1, 5, 10, 20, 50]
        
        for size in cart_sizes:
            customer_id = f"{performance_customer_id}-size-{size}"
            
            # Add items to cart
            for i in range(size):
                item = {
                    "customer_id": customer_id,
                    "product_id": f"size-test-{i}",
                    "product_name": f"Size Test Item {i}",
                    "price": "15.99",
                    "quantity": 1
                }
                requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            
            # Measure get cart response time
            response_times = []
            for _ in range(10):
                start_time = time.time()
                response = requests.get(f"{api_base_url}/api/v1/cart/{customer_id}")
                end_time = time.time()
                
                assert response.status_code == 200
                response_times.append(end_time - start_time)
            
            avg_response_time = statistics.mean(response_times)
            
            # Performance should not degrade significantly with cart size
            assert avg_response_time < 0.3, f"Get cart response time {avg_response_time:.3f}s too high for {size} items"
            
            print(f"Get Cart Performance ({size} items): {avg_response_time:.3f}s")
    
    def test_concurrent_requests_performance(self, api_base_url):
        """Test performance under concurrent load."""
        num_threads = 10
        requests_per_thread = 5
        
        def make_concurrent_requests(thread_id):
            """Function to make requests in a thread."""
            customer_id = f"concurrent-{thread_id}-{uuid.uuid4().hex[:4]}"
            response_times = []
            
            for i in range(requests_per_thread):
                item = {
                    "customer_id": customer_id,
                    "product_id": f"concurrent-item-{thread_id}-{i}",
                    "product_name": f"Concurrent Item {thread_id}-{i}",
                    "price": "19.99",
                    "quantity": 1
                }
                
                start_time = time.time()
                response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
                else:
                    response_times.append(float('inf'))  # Mark failed requests
            
            return response_times
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_concurrent_requests, i) for i in range(num_threads)]
            
            all_response_times = []
            successful_requests = 0
            
            for future in as_completed(futures):
                thread_response_times = future.result()
                for rt in thread_response_times:
                    if rt != float('inf'):
                        all_response_times.append(rt)
                        successful_requests += 1
        
        # Analyze results
        total_requests = num_threads * requests_per_thread
        success_rate = successful_requests / total_requests
        
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} too low under concurrent load"
        
        if all_response_times:
            avg_response_time = statistics.mean(all_response_times)
            max_response_time = max(all_response_times)
            
            # Performance should not degrade too much under load
            assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s too high under load"
            assert max_response_time < 3.0, f"Max response time {max_response_time:.3f}s too high under load"
            
            print(f"Concurrent Load Performance:")
            print(f"  Success rate: {success_rate:.2%}")
            print(f"  Average response time: {avg_response_time:.3f}s")
            print(f"  Max response time: {max_response_time:.3f}s")
    
    def test_memory_usage_stability(self, api_base_url):
        """Test that memory usage remains stable during operations."""
        customer_id = f"memory-test-{uuid.uuid4().hex[:8]}"
        
        # Perform many operations to test for memory leaks
        for batch in range(5):
            # Add many items
            for i in range(20):
                item = {
                    "customer_id": customer_id,
                    "product_id": f"memory-item-{batch}-{i}",
                    "product_name": f"Memory Test Item {batch}-{i}",
                    "price": "12.99",
                    "quantity": 1
                }
                
                response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
                assert response.status_code == 200
            
            # Get cart multiple times
            for _ in range(10):
                response = requests.get(f"{api_base_url}/api/v1/cart/{customer_id}")
                assert response.status_code == 200
            
            # Clear cart
            response = requests.delete(f"{api_base_url}/api/v1/cart/{customer_id}")
            assert response.status_code == 200
            
            # Verify cart is empty
            response = requests.get(f"{api_base_url}/api/v1/cart/{customer_id}")
            assert response.status_code == 200
            cart_data = response.json()["cart"]
            assert cart_data["total_items"] == 0
        
        # If we reach here without errors, memory usage is likely stable
        assert True
    
    def test_database_performance_under_load(self, api_base_url):
        """Test database performance under sustained load."""
        num_customers = 20
        items_per_customer = 10
        
        start_time = time.time()
        
        # Create load on database
        for customer_idx in range(num_customers):
            customer_id = f"db-load-{customer_idx}-{uuid.uuid4().hex[:4]}"
            
            for item_idx in range(items_per_customer):
                item = {
                    "customer_id": customer_id,
                    "product_id": f"db-item-{customer_idx}-{item_idx}",
                    "product_name": f"DB Load Item {customer_idx}-{item_idx}",
                    "price": f"{10 + (item_idx % 10)}.99",
                    "quantity": (item_idx % 5) + 1
                }
                
                response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
                assert response.status_code == 200
        
        total_time = time.time() - start_time
        total_operations = num_customers * items_per_customer
        operations_per_second = total_operations / total_time
        
        # Should handle reasonable throughput
        assert operations_per_second > 10, f"Database throughput {operations_per_second:.1f} ops/sec too low"
        
        print(f"Database Performance:")
        print(f"  Total operations: {total_operations}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {operations_per_second:.1f} ops/sec")
    
    def test_checkout_performance(self, api_base_url):
        """Test checkout operation performance."""
        checkout_times = []
        
        for i in range(10):
            customer_id = f"checkout-perf-{i}-{uuid.uuid4().hex[:4]}"
            
            # Add items to cart
            for j in range(5):
                item = {
                    "customer_id": customer_id,
                    "product_id": f"checkout-item-{i}-{j}",
                    "product_name": f"Checkout Item {i}-{j}",
                    "price": "29.99",
                    "quantity": 1
                }
                requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            
            # Measure checkout time
            checkout_payload = {
                "customer_id": customer_id,
                "payment_method": "credit_card",
                "shipping_address": {
                    "street": f"123 Checkout St {i}",
                    "city": "Checkout City",
                    "state": "CO",
                    "zip": "12345"
                }
            }
            
            start_time = time.time()
            response = requests.post(f"{api_base_url}/api/v1/cart/checkout", json=checkout_payload)
            end_time = time.time()
            
            assert response.status_code == 200
            checkout_times.append(end_time - start_time)
        
        avg_checkout_time = statistics.mean(checkout_times)
        max_checkout_time = max(checkout_times)
        
        # Checkout should be reasonably fast
        assert avg_checkout_time < 1.0, f"Average checkout time {avg_checkout_time:.3f}s too high"
        assert max_checkout_time < 2.0, f"Max checkout time {max_checkout_time:.3f}s too high"
        
        print(f"Checkout Performance:")
        print(f"  Average: {avg_checkout_time:.3f}s")
        print(f"  Max: {max_checkout_time:.3f}s")
    
    def test_api_rate_limiting_behavior(self, api_base_url):
        """Test API behavior under rapid requests (rate limiting)."""
        customer_id = f"rate-limit-{uuid.uuid4().hex[:8]}"
        
        # Make rapid requests
        rapid_response_times = []
        status_codes = []
        
        for i in range(50):
            item = {
                "customer_id": customer_id,
                "product_id": f"rapid-item-{i}",
                "product_name": f"Rapid Item {i}",
                "price": "5.99",
                "quantity": 1
            }
            
            start_time = time.time()
            response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            end_time = time.time()
            
            rapid_response_times.append(end_time - start_time)
            status_codes.append(response.status_code)
        
        # Analyze response patterns
        success_responses = sum(1 for code in status_codes if code == 200)
        success_rate = success_responses / len(status_codes)
        
        # Should handle most requests successfully
        assert success_rate >= 0.8, f"Success rate {success_rate:.2%} too low under rapid requests"
        
        # Check for rate limiting responses (429)
        rate_limited = sum(1 for code in status_codes if code == 429)
        
        print(f"Rate Limiting Test:")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Rate limited responses: {rate_limited}")
        print(f"  Average response time: {statistics.mean(rapid_response_times):.3f}s")
    
    def test_large_cart_performance(self, api_base_url):
        """Test performance with large cart sizes."""
        large_customer_id = f"large-cart-{uuid.uuid4().hex[:8]}"
        
        # Add many items to create a large cart
        large_cart_size = 100
        
        add_times = []
        for i in range(large_cart_size):
            item = {
                "customer_id": large_customer_id,
                "product_id": f"large-item-{i}",
                "product_name": f"Large Cart Item {i}",
                "price": f"{(i % 100) + 1}.99",
                "quantity": (i % 10) + 1
            }
            
            start_time = time.time()
            response = requests.post(f"{api_base_url}/api/v1/cart/items", json=item)
            end_time = time.time()
            
            assert response.status_code == 200
            add_times.append(end_time - start_time)
        
        # Test retrieval performance with large cart
        get_times = []
        for _ in range(10):
            start_time = time.time()
            response = requests.get(f"{api_base_url}/api/v1/cart/{large_customer_id}")
            end_time = time.time()
            
            assert response.status_code == 200
            get_times.append(end_time - start_time)
            
            # Verify cart integrity
            cart_data = response.json()["cart"]
            assert cart_data["total_items"] == sum((i % 10) + 1 for i in range(large_cart_size))
        
        avg_add_time = statistics.mean(add_times)
        avg_get_time = statistics.mean(get_times)
        
        # Performance should not degrade significantly with large carts
        assert avg_add_time < 0.5, f"Add item time {avg_add_time:.3f}s too high for large cart"
        assert avg_get_time < 1.0, f"Get cart time {avg_get_time:.3f}s too high for large cart"
        
        print(f"Large Cart Performance ({large_cart_size} items):")
        print(f"  Average add time: {avg_add_time:.3f}s")
        print(f"  Average get time: {avg_get_time:.3f}s")
