#!/usr/bin/env python3
"""
Test script for checkout functionality
"""

import requests
import json
import time

# API Configuration
API_BASE_URL = 'https://mk8ppghx0d.execute-api.us-east-1.amazonaws.com/prod'

def test_checkout_flow():
    """Test the complete checkout flow"""
    print("🧪 Testing Complete Checkout Flow")
    print("=" * 50)
    
    customer_id = "test-checkout-customer-" + str(int(time.time()))
    
    # Step 1: Add items to cart
    print("\n1️⃣ Adding items to cart...")
    
    items_to_add = [
        {
            "customer_id": customer_id,
            "product_id": "laptop-001",
            "product_name": "MacBook Pro 16-inch",
            "price": "2499.99",
            "quantity": 1
        },
        {
            "customer_id": customer_id,
            "product_id": "mouse-001",
            "product_name": "Magic Mouse",
            "price": "79.99",
            "quantity": 2
        }
    ]
    
    cart_total = 0
    for item in items_to_add:
        try:
            response = requests.post(
                f"{API_BASE_URL}/cart/items",
                headers={"Content-Type": "application/json"},
                json=item,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Added {item['product_name']} - Quantity: {item['quantity']}")
                    cart_total = float(data['cart']['subtotal'])
                else:
                    print(f"❌ Failed to add {item['product_name']}: {data.get('error')}")
                    return False
            else:
                print(f"❌ HTTP Error {response.status_code} adding {item['product_name']}")
                return False
                
        except Exception as e:
            print(f"❌ Exception adding {item['product_name']}: {e}")
            return False
    
    print(f"🛒 Cart total: ${cart_total:.2f}")
    
    # Step 2: Process checkout
    print("\n2️⃣ Processing checkout...")
    
    checkout_data = {
        "customer_id": customer_id,
        "payment_method": "credit_card",
        "shipping_address": {
            "street": "123 Test Street",
            "city": "San Francisco",
            "state": "CA",
            "zip": "94105",
            "country": "US"
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/cart/checkout",
            headers={"Content-Type": "application/json"},
            json=checkout_data,
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Checkout successful!")
                print(f"📋 Order ID: {data.get('order_id')}")
                print(f"💰 Total Amount: ${data.get('total_amount')}")
                
                # Step 3: Verify cart is cleared
                print("\n3️⃣ Verifying cart is cleared...")
                
                # Try to add another item to see if cart was cleared
                verify_item = {
                    "customer_id": customer_id,
                    "product_id": "keyboard-001",
                    "product_name": "Mechanical Keyboard",
                    "price": "129.99",
                    "quantity": 1
                }
                
                verify_response = requests.post(
                    f"{API_BASE_URL}/cart/items",
                    headers={"Content-Type": "application/json"},
                    json=verify_item,
                    timeout=10
                )
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    if verify_data.get('success'):
                        new_cart = verify_data['cart']
                        if len(new_cart['items']) == 1 and new_cart['items'][0]['product_id'] == 'keyboard-001':
                            print("✅ Cart was properly cleared after checkout")
                            return True
                        else:
                            print("❌ Cart was not properly cleared")
                            return False
                    else:
                        print(f"❌ Failed to verify cart clearing: {verify_data.get('error')}")
                        return False
                else:
                    print(f"❌ HTTP Error {verify_response.status_code} during verification")
                    return False
                    
            else:
                print(f"❌ Checkout failed: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code} during checkout")
            return False
            
    except Exception as e:
        print(f"❌ Exception during checkout: {e}")
        return False

def test_checkout_edge_cases():
    """Test checkout edge cases"""
    print("\n🧪 Testing Checkout Edge Cases")
    print("=" * 50)
    
    # Test 1: Checkout with empty cart
    print("\n1️⃣ Testing checkout with empty cart...")
    empty_cart_customer = "empty-cart-customer-" + str(int(time.time()))
    
    checkout_data = {
        "customer_id": empty_cart_customer,
        "payment_method": "credit_card"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/cart/checkout",
            headers={"Content-Type": "application/json"},
            json=checkout_data,
            timeout=10
        )
        
        if response.status_code == 400:
            data = response.json()
            if "empty" in data.get('error', '').lower():
                print("✅ Empty cart checkout properly rejected")
            else:
                print(f"❌ Unexpected error for empty cart: {data.get('error')}")
        else:
            print(f"❌ Expected 400 status for empty cart, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception testing empty cart: {e}")
    
    # Test 2: Checkout with missing customer_id
    print("\n2️⃣ Testing checkout with missing customer_id...")
    
    invalid_checkout_data = {
        "payment_method": "credit_card"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/cart/checkout",
            headers={"Content-Type": "application/json"},
            json=invalid_checkout_data,
            timeout=10
        )
        
        if response.status_code == 400:
            data = response.json()
            if "customer" in data.get('error', '').lower():
                print("✅ Missing customer_id properly rejected")
            else:
                print(f"❌ Unexpected error for missing customer_id: {data.get('error')}")
        else:
            print(f"❌ Expected 400 status for missing customer_id, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception testing missing customer_id: {e}")

if __name__ == "__main__":
    print("🛒 Shopping Cart Checkout Test Suite")
    print("=" * 60)
    
    # Test complete checkout flow
    success = test_checkout_flow()
    
    # Test edge cases
    test_checkout_edge_cases()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All checkout tests completed successfully!")
    else:
        print("❌ Some checkout tests failed. Check the logs above.")
    print("=" * 60)
