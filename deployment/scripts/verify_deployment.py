#!/usr/bin/env python3
"""
Deployment verification script for Shopping Cart microservices.
Tests both frontend and backend services after deployment.
"""

import requests
import json
import sys
import time
from typing import Dict, Any


def test_backend_health(backend_url: str) -> bool:
    """Test backend health endpoint."""
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend health check passed: {health_data['status']}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False


def test_frontend_health(frontend_url: str) -> bool:
    """Test frontend health endpoint."""
    try:
        response = requests.get(f"{frontend_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend health check passed")
            return True
        else:
            print(f"❌ Frontend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend health check error: {e}")
        return False


def test_cart_operations(backend_url: str) -> bool:
    """Test cart operations via backend API."""
    try:
        # Test data
        test_item = {
            "customer_id": "test-customer-123",
            "product_id": "test-product-456",
            "product_name": "Test Gaming Laptop",
            "price": "1299.99",
            "quantity": 1
        }
        
        # Add item to cart
        print("🧪 Testing add item to cart...")
        response = requests.post(
            f"{backend_url}/api/v1/cart/items",
            json=test_item,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Add item failed: {response.status_code} - {response.text}")
            return False
        
        add_result = response.json()
        if not add_result.get("success"):
            print(f"❌ Add item failed: {add_result}")
            return False
        
        print("✅ Add item to cart successful")
        
        # Get cart
        print("🧪 Testing get cart...")
        response = requests.get(
            f"{backend_url}/api/v1/cart/{test_item['customer_id']}",
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Get cart failed: {response.status_code}")
            return False
        
        cart_result = response.json()
        if not cart_result.get("success"):
            print(f"❌ Get cart failed: {cart_result}")
            return False
        
        cart = cart_result["cart"]
        if cart["total_items"] != 1:
            print(f"❌ Cart should have 1 item, has {cart['total_items']}")
            return False
        
        print("✅ Get cart successful")
        
        # Clear cart
        print("🧪 Testing clear cart...")
        response = requests.delete(
            f"{backend_url}/api/v1/cart/{test_item['customer_id']}",
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Clear cart failed: {response.status_code}")
            return False
        
        clear_result = response.json()
        if not clear_result.get("success"):
            print(f"❌ Clear cart failed: {clear_result}")
            return False
        
        print("✅ Clear cart successful")
        return True
        
    except Exception as e:
        print(f"❌ Cart operations test error: {e}")
        return False


def test_frontend_loads(frontend_url: str) -> bool:
    """Test that frontend loads properly."""
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200 and "Shopping Cart" in response.text:
            print("✅ Frontend loads successfully")
            return True
        else:
            print(f"❌ Frontend load failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend load error: {e}")
        return False


def main():
    """Main verification function."""
    if len(sys.argv) < 3:
        print("Usage: python verify_deployment.py <frontend_url> <backend_url>")
        print("Example: python verify_deployment.py http://frontend-alb.com http://backend-alb.com:8000")
        sys.exit(1)
    
    frontend_url = sys.argv[1].rstrip('/')
    backend_url = sys.argv[2].rstrip('/')
    
    print("🚀 Starting deployment verification...")
    print(f"Frontend URL: {frontend_url}")
    print(f"Backend URL: {backend_url}")
    print("-" * 50)
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)
    
    tests_passed = 0
    total_tests = 4
    
    # Test backend health
    if test_backend_health(backend_url):
        tests_passed += 1
    
    # Test frontend health
    if test_frontend_health(frontend_url):
        tests_passed += 1
    
    # Test cart operations
    if test_cart_operations(backend_url):
        tests_passed += 1
    
    # Test frontend loads
    if test_frontend_loads(frontend_url):
        tests_passed += 1
    
    print("-" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Deployment is successful.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
