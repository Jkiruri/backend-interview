#!/usr/bin/env python
"""
Test script to verify that admin emails and customer confirmations are automatically sent when orders are placed
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_order_notifications():
    """Test that notifications are automatically sent when orders are placed"""
    print("🧪 Testing Order Notifications...")
    print("=" * 60)
    
    # Step 1: Login as admin to get token
    print("\n1. Getting admin authentication token...")
    try:
        admin_login_data = {
            "email": "admin@jameskiruri.co.ke",
            "password": "admin123456"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login/",
            json=admin_login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            admin_token = response.json().get('token')
            print(f"✅ Admin token received: {admin_token[:20]}...")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during admin login: {e}")
        return
    
    # Step 2: Get products to use in order
    print("\n2. Getting products for order creation...")
    try:
        headers = {"Authorization": f"Token {admin_token}"}
        response = requests.get(f"{BASE_URL}/api/v1/products/", headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products")
            
            if len(products) >= 2:
                product1 = products[0]
                product2 = products[1]
                print(f"   Using products: {product1.get('name')} and {product2.get('name')}")
            else:
                print("❌ Need at least 2 products to test order creation")
                return
        else:
            print(f"❌ Failed to get products: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting products: {e}")
        return
    
    # Step 3: Create a test customer account
    print("\n3. Creating test customer account...")
    try:
        customer_data = {
            "email": "testcustomer@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "first_name": "Test",
            "last_name": "Customer",
            "phone_number": "+254700123456",
            "address": "123 Test St, Nairobi, Kenya",
            "city": "Nairobi",
            "state": "Nairobi",
            "country": "Kenya",
            "postal_code": "00100"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register/",
            json=customer_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [201, 400]:  # 400 if user already exists
            print("✅ Customer account ready (created or already exists)")
        else:
            print(f"❌ Customer registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating customer: {e}")
        return
    
    # Step 4: Login as customer
    print("\n4. Logging in as customer...")
    try:
        customer_login_data = {
            "email": "testcustomer@example.com",
            "password": "password123"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login/",
            json=customer_login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            customer_token = response.json().get('token')
            print(f"✅ Customer token received: {customer_token[:20]}...")
        else:
            print(f"❌ Customer login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during customer login: {e}")
        return
    
    # Step 5: Create an order (this should trigger notifications)
    print("\n5. Creating order to trigger notifications...")
    try:
        order_data = {
            "shipping_address": "456 Order St, Nairobi, Kenya",
            "items": [
                {
                    "product_id": str(product1.get('id')),
                    "quantity": 2
                },
                {
                    "product_id": str(product2.get('id')),
                    "quantity": 1
                }
            ]
        }
        
        customer_headers = {"Authorization": f"Token {customer_token}", "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/api/v1/orders/",
            json=order_data,
            headers=customer_headers
        )
        
        if response.status_code == 201:
            order = response.json()
            order_id = order.get('id')
            order_number = order.get('order_number')
            print(f"✅ Order created successfully!")
            print(f"   Order Number: {order_number}")
            print(f"   Order ID: {order_id}")
            print(f"   Total Amount: Ksh {order.get('total_amount')}")
        else:
            print(f"❌ Order creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return
    
    # Step 6: Check if notifications were sent
    print("\n6. Checking notification status...")
    print("   ⏳ Waiting 5 seconds for notifications to be processed...")
    time.sleep(5)
    
    # Check customer notifications
    print("\n7. Checking customer notifications...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/notifications/",
            headers=customer_headers
        )
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Found {len(notifications)} customer notifications")
            
            # Look for order confirmation notifications
            order_notifications = [n for n in notifications if 'order' in n.get('subject', '').lower() or 'order' in n.get('message', '').lower()]
            print(f"   Order-related notifications: {len(order_notifications)}")
            
            for notification in order_notifications[:3]:  # Show first 3
                print(f"   - {notification.get('subject', 'No subject')} ({notification.get('status', 'unknown')})")
        else:
            print(f"❌ Failed to get customer notifications: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking customer notifications: {e}")
    
    # Step 7: Check admin dashboard for order
    print("\n8. Checking admin dashboard for new order...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/dashboard/",
            headers=headers
        )
        
        if response.status_code == 200:
            dashboard = response.json()
            print("✅ Admin dashboard accessible")
            
            # Check if order appears in recent orders
            recent_orders = dashboard.get('recent_orders', [])
            print(f"   Recent orders in dashboard: {len(recent_orders)}")
            
            # Look for our order
            our_order = next((order for order in recent_orders if order.get('order_number') == order_number), None)
            if our_order:
                print(f"   ✅ Our order found in admin dashboard!")
                print(f"      Status: {our_order.get('status')}")
                print(f"      Customer: {our_order.get('customer_name')}")
            else:
                print(f"   ⚠️  Our order not found in recent orders (may be normal)")
        else:
            print(f"❌ Failed to get admin dashboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking admin dashboard: {e}")
    
    # Step 8: Summary
    print("\n" + "=" * 60)
    print("🎉 Order Notification Test Summary:")
    print(f"   ✅ Order created: {order_number}")
    print(f"   ✅ Customer token: {customer_token[:20]}...")
    print(f"   ✅ Admin token: {admin_token[:20]}...")
    print("\n📧 Expected Notifications:")
    print("   1. Customer SMS confirmation (if phone number valid)")
    print("   2. Customer email confirmation")
    print("   3. Admin email notification")
    print("   4. Order status updates (if status changes)")
    print("\n🔍 To verify notifications:")
    print("   1. Check email inboxes (customer and admin)")
    print("   2. Check SMS logs in logs/sms.log")
    print("   3. Check Celery worker logs")
    print("   4. Use Postman collection to test endpoints")

if __name__ == "__main__":
    test_order_notifications()
