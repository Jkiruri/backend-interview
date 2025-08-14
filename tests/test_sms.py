#!/usr/bin/env python
"""
Test script for Africa's Talking SMS functionality
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from notifications.notification_manager import NotificationManager
from notifications.sms_service import SMSService

Customer = get_user_model()

BASE_URL = "http://localhost:8000/api/v1"

def test_sms_service_direct():
    """Test SMS service directly"""
    print("=== Testing SMS Service Directly ===")
    
    # Initialize SMS service
    sms_service = SMSService()
    
    # Test phone number (replace with your actual phone number)
    test_phone = "+254700123456"  # TODO: Replace with your actual phone number
    test_message = "Hello from OrderFlow! This is a test SMS from Africa's Talking."
    
    print(f"Sending SMS to: {test_phone}")
    print(f"Message: {test_message}")
    
    # Send SMS
    result = sms_service.send_sms(test_phone, test_message)
    
    print(f"Result: {result}")
    
    if result['success']:
        print("✅ SMS sent successfully!")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   Cost: {result.get('cost')}")
    else:
        print("❌ SMS failed!")
        print(f"   Error: {result.get('error')}")
    
    return result

def test_sms_via_api():
    """Test SMS via API endpoint"""
    print("\n=== Testing SMS via API ===")
    
    # First, login to get token
    login_data = {
        "email": "john.doe@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code != 200:
        print("❌ Login failed")
        return None
    
    token = response.json().get('token')
    headers = {"Authorization": f"Token {token}"}
    
    # Test phone number (replace with your actual phone number)
    test_phone = "+254700123456"  # TODO: Replace with your actual phone number
    test_message = "Hello from OrderFlow API! This is a test SMS."
    
    # Send test SMS via API
    sms_data = {
        "phone_number": test_phone,
        "message": test_message
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/notifications/send_test_sms/",
        json=sms_data,
        headers=headers
    )
    
    print(f"API Response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ SMS sent successfully via API!")
    else:
        print("❌ SMS failed via API!")
    
    return response.json()

def test_notification_manager():
    """Test notification manager"""
    print("\n=== Testing Notification Manager ===")
    
    # Get a customer
    try:
        customer = Customer.objects.get(email="john.doe@example.com")
        print(f"Testing with customer: {customer.full_name}")
        
        # Test custom notification
        notification_manager = NotificationManager()
        result = notification_manager.send_custom_notification(
            customer=customer,
            message="Test notification from OrderFlow notification manager!",
            subject="Test Notification",
            send_sms=True,
            send_email=False  # Disable email for this test
        )
        
        print(f"Notification Manager Result: {result}")
        
        if result['success']:
            print("✅ Notification sent successfully!")
        else:
            print("❌ Notification failed!")
            print(f"   Error: {result.get('error')}")
        
        return result
        
    except Customer.DoesNotExist:
        print("❌ Test customer not found")
        return None

def test_order_notification():
    """Test order notification (requires existing order)"""
    print("\n=== Testing Order Notification ===")
    
    from orders.models import Order
    
    # Get the first order
    try:
        order = Order.objects.first()
        if order:
            print(f"Testing with order: {order.order_number}")
            
            notification_manager = NotificationManager()
            result = notification_manager.send_order_confirmation(order)
            
            print(f"Order Notification Result: {result}")
            
            if result['success']:
                print("✅ Order notification sent successfully!")
            else:
                print("❌ Order notification failed!")
                print(f"   Error: {result.get('error')}")
            
            return result
        else:
            print("❌ No orders found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error testing order notification: {e}")
        return None

def check_notification_stats():
    """Check notification statistics"""
    print("\n=== Notification Statistics ===")
    
    from notifications.models import Notification
    
    total = Notification.objects.count()
    sms_count = Notification.objects.filter(notification_type='sms').count()
    email_count = Notification.objects.filter(notification_type='email').count()
    pending = Notification.objects.filter(status='pending').count()
    sent = Notification.objects.filter(status='sent').count()
    failed = Notification.objects.filter(status='failed').count()
    
    print(f"Total notifications: {total}")
    print(f"SMS notifications: {sms_count}")
    print(f"Email notifications: {email_count}")
    print(f"Pending: {pending}")
    print(f"Sent: {sent}")
    print(f"Failed: {failed}")
    
    # Show recent notifications
    recent = Notification.objects.order_by('-created_at')[:5]
    print("\nRecent notifications:")
    for notification in recent:
        print(f"  - {notification.notification_type.upper()} to {notification.recipient.email}: {notification.status}")

def main():
    """Run all SMS tests"""
    print("🚀 Testing Africa's Talking SMS Integration")
    print("=" * 60)
    
    # Check if Africa's Talking credentials are configured
    from django.conf import settings
    print(f"Africa's Talking Username: {settings.AFRICASTALKING_USERNAME}")
    print(f"Africa's Talking Sender ID: {settings.AFRICASTALKING_SENDER_ID}")
    print(f"API Key configured: {'Yes' if settings.AFRICASTALKING_API_KEY != 'your-api-key' else 'No'}")
    print()
    
    # Run tests
    sms_result = test_sms_service_direct()
    api_result = test_sms_via_api()
    manager_result = test_notification_manager()
    order_result = test_order_notification()
    check_notification_stats()
    
    print("\n" + "=" * 60)
    print("🎉 SMS Testing Completed!")
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"   - Direct SMS Service: {'✅ Passed' if sms_result and sms_result.get('success') else '❌ Failed'}")
    print(f"   - API SMS Endpoint: {'✅ Passed' if api_result and 'message' in api_result else '❌ Failed'}")
    print(f"   - Notification Manager: {'✅ Passed' if manager_result and manager_result.get('success') else '❌ Failed'}")
    print(f"   - Order Notification: {'✅ Passed' if order_result and order_result.get('success') else '❌ Failed'}")
    
    print("\n🔧 Troubleshooting:")
    print("   - Make sure Africa's Talking credentials are set in .env file")
    print("   - Verify the phone number is in international format (+254...)")
    print("   - Check Africa's Talking account has sufficient credits")
    print("   - Ensure the sender ID is approved by Africa's Talking")

if __name__ == "__main__":
    main()
