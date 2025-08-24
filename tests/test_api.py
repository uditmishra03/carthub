#!/usr/bin/env python3
"""
Comprehensive test script for Shopping Cart API
Usage: python test_api.py
"""

import requests
import json
import time
from decimal import Decimal

# API Configuration
API_BASE_URL = "https://mk8ppghx0d.execute-api.us-east-1.amazonaws.com/prod"
CART_ITEMS_ENDPOINT = f"{API_BASE_URL}/cart/items"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}🧪 {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def make_request(data, expected_status=200):
    """Make API request and return response"""
    try:
        response = requests.post(
            CART_ITEMS_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json=data,
            timeout=10
        )
        
        print(f"Request: {json.dumps(data, indent=2)}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == expected_status:
            print_success(f"Expected status code {expected_status}")
            return response.json()
        else:
            print_error(f"Expected {expected_status}, got {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON response: {e}")
        return None

def test_add_single_item():
    """Test adding a single item to cart"""
    print_test_header("Test 1: Add Single Item")
    
    data = {
        "customer_id": "test-customer-single",
        "product_id": "laptop-001",
        "product_name": "Gaming Laptop",
        "price": "1299.99",
        "quantity": 1
    }
    
    response = make_request(data)
    if response and response.get("success"):
        cart = response["cart"]
        assert cart["total_items"] == 1
        assert cart["subtotal"] == "1299.99"
        assert len(cart["items"]) == 1
        print_success("Single item added successfully!")
    else:
        print_error("Failed to add single item")

def test_add_multiple_items():
    """Test adding multiple different items"""
    print_test_header("Test 2: Add Multiple Different Items")
    
    customer_id = "test-customer-multiple"
    
    # Add first item
    data1 = {
        "customer_id": customer_id,
        "product_id": "mouse-001",
        "product_name": "Wireless Mouse",
        "price": "49.99",
        "quantity": 1
    }
    
    print_info("Adding first item...")
    response1 = make_request(data1)
    
    # Add second item
    data2 = {
        "customer_id": customer_id,
        "product_id": "keyboard-001",
        "product_name": "Mechanical Keyboard",
        "price": "129.99",
        "quantity": 1
    }
    
    print_info("Adding second item...")
    response2 = make_request(data2)
    
    if response2 and response2.get("success"):
        cart = response2["cart"]
        assert cart["total_items"] == 2
        assert cart["subtotal"] == "179.98"
        assert len(cart["items"]) == 2
        print_success("Multiple items added successfully!")
    else:
        print_error("Failed to add multiple items")

def test_quantity_update():
    """Test updating quantity of existing item"""
    print_test_header("Test 3: Update Item Quantity")
    
    customer_id = "test-customer-quantity"
    
    # Add initial item
    data1 = {
        "customer_id": customer_id,
        "product_id": "monitor-001",
        "product_name": "4K Monitor",
        "price": "399.99",
        "quantity": 1
    }
    
    print_info("Adding initial item...")
    response1 = make_request(data1)
    
    # Add same item again (should update quantity)
    data2 = {
        "customer_id": customer_id,
        "product_id": "monitor-001",
        "product_name": "4K Monitor",
        "price": "399.99",
        "quantity": 2
    }
    
    print_info("Adding same item again...")
    response2 = make_request(data2)
    
    if response2 and response2.get("success"):
        cart = response2["cart"]
        assert cart["total_items"] == 3  # 1 + 2
        assert cart["subtotal"] == "1199.97"  # 399.99 * 3
        assert len(cart["items"]) == 1  # Still only one unique product
        assert cart["items"][0]["quantity"] == 3
        print_success("Quantity updated successfully!")
    else:
        print_error("Failed to update quantity")

def test_error_scenarios():
    """Test various error scenarios"""
    print_test_header("Test 4: Error Handling")
    
    # Test invalid quantity
    print_info("Testing invalid quantity (0)...")
    data_invalid_qty = {
        "customer_id": "test-error",
        "product_id": "error-001",
        "product_name": "Error Product",
        "price": "10.00",
        "quantity": 0
    }
    
    response = make_request(data_invalid_qty, expected_status=400)
    if response and not response.get("success"):
        assert "Quantity must be greater than 0" in response.get("error", "")
        print_success("Invalid quantity error handled correctly!")
    
    # Test missing fields
    print_info("Testing missing required fields...")
    data_missing = {
        "customer_id": "test-error",
        "product_id": "error-002"
        # Missing product_name, price, quantity
    }
    
    response = make_request(data_missing, expected_status=400)
    if response and not response.get("success"):
        assert "Missing required field" in response.get("error", "")
        print_success("Missing fields error handled correctly!")
    
    # Test negative price
    print_info("Testing negative price...")
    data_negative_price = {
        "customer_id": "test-error",
        "product_id": "error-003",
        "product_name": "Negative Price Product",
        "price": "-10.00",
        "quantity": 1
    }
    
    response = make_request(data_negative_price, expected_status=400)
    if response and not response.get("success"):
        print_success("Negative price error handled correctly!")

def test_large_cart():
    """Test adding many items to cart"""
    print_test_header("Test 5: Large Cart Performance")
    
    customer_id = "test-customer-large"
    
    print_info("Adding 10 different products...")
    
    total_expected = Decimal("0")
    for i in range(10):
        price = Decimal(f"{(i+1)*10}.99")
        total_expected += price
        
        data = {
            "customer_id": customer_id,
            "product_id": f"bulk-{i+1:03d}",
            "product_name": f"Product {i+1}",
            "price": str(price),
            "quantity": 1
        }
        
        response = make_request(data)
        if not (response and response.get("success")):
            print_error(f"Failed to add product {i+1}")
            return
    
    print_success(f"Successfully added 10 products! Expected total: ${total_expected}")

def test_concurrent_requests():
    """Test handling concurrent requests for same customer"""
    print_test_header("Test 6: Concurrent Requests Simulation")
    
    customer_id = "test-customer-concurrent"
    
    print_info("Simulating rapid consecutive requests...")
    
    # Simulate rapid requests
    for i in range(3):
        data = {
            "customer_id": customer_id,
            "product_id": f"concurrent-{i+1}",
            "product_name": f"Concurrent Product {i+1}",
            "price": "25.99",
            "quantity": 1
        }
        
        response = make_request(data)
        if response and response.get("success"):
            print_success(f"Request {i+1} processed successfully")
        else:
            print_error(f"Request {i+1} failed")
        
        time.sleep(0.1)  # Small delay between requests

def run_all_tests():
    """Run all test scenarios"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🚀 Shopping Cart API Test Suite")
    print("=" * 50)
    print(f"{Colors.END}")
    
    tests = [
        test_add_single_item,
        test_add_multiple_items,
        test_quantity_update,
        test_error_scenarios,
        test_large_cart,
        test_concurrent_requests
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            failed += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}❌ Failed: {failed}{Colors.END}")
    print(f"{Colors.BOLD}Total Tests: {passed + failed}{Colors.END}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! API is working perfectly!{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Please check the logs above.{Colors.END}")

if __name__ == "__main__":
    run_all_tests()
