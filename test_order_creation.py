#!/usr/bin/env python3
"""
Test script to verify order creation works with UUID product IDs
"""
import requests
import json
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from products.models import Product
from customers.models import Customer

def test_order_creation():
    """Test order creation with UUID product IDs"""
    
    # First, let's get a product ID from the database
    try:
        product = Product.objects.filter(status='active').first()
        if not product:
            print("❌ No active products found in database")
            return
        
        print(f"✅ Found product: {product.name} (ID: {product.id})")
        
        # Test order creation
        url = "http://localhost:8000/api/v1/orders/"
        
        # Create test user if needed
        user, created = Customer.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_verified': True,
                'is_active': True
            }
        )
        if created:
            user.set_password('testpassword123')
            user.save()
            print(f"✅ Created test user: {user.email}")
        
        # Login to get token
        login_url = "http://localhost:8000/api/v1/auth/login/"
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        login_response = requests.post(login_url, json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()['token']
        print(f"✅ Login successful, got token")
        
        # Create order data
        order_data = {
            "shipping_address": "123 Test Street, Test City",
            "billing_address": "123 Test Street, Test City",
            "phone_number": "+254700000000",
            "notes": "Test order",
            "payment_method": "cash",
            "items": [
                {
                    "product_id": str(product.id),  # Convert UUID to string
                    "quantity": 1
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {token}"
        }
        
        # Create order
        response = requests.post(url, json=order_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Order creation successful!")
            order_data = response.json()
            print(f"Order ID: {order_data['id']}")
            print(f"Order Number: {order_data['order_number']}")
        elif response.status_code == 400:
            print("⚠️  Order creation failed - validation error")
            errors = response.json()
            if 'items' in errors:
                for item_error in errors['items']:
                    if 'product_id' in item_error:
                        print(f"Product ID error: {item_error['product_id']}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_order_creation()
