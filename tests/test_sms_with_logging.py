#!/usr/bin/env python
"""
Comprehensive SMS test script with detailed logging
"""
import os
import django
import time

# Setup Django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from notifications.sms_service import SMSService
from notifications.notification_manager import NotificationManager
from django.contrib.auth import get_user_model
from orders.models import Order
from django.conf import settings
import logging

Customer = get_user_model()
logger = logging.getLogger(__name__)

def test_sms_with_logging():
    """Test SMS with detailed logging"""
    print("🚀 Testing SMS with Detailed Logging")
    print("=" * 50)
    
    # Check configuration
    print(f"Username: {settings.AFRICASTALKING_USERNAME}")
    print(f"API Key: {settings.AFRICASTALKING_API_KEY[:20]}...")
    print(f"Sender ID: {settings.AFRICASTALKING_SENDER_ID}")
    print()
    
    # Initialize SMS service
    sms_service = SMSService()
    
    # Test phone number (replace with your actual phone number)
    test_phone = "+254700123456"  # Replace this with your phone number
    test_message = "Hello from OrderFlow! This is a test SMS with detailed logging."
    
    print(f"Sending SMS to: {test_phone}")
    print(f"Message: {test_message}")
    print()
    
    # Send SMS
    result = sms_service.send_sms(test_phone, test_message)
    
    print(f"Result: {result}")
    print()
    
    if result['success']:
        print("✅ SMS sent successfully!")
        print(f"   Message ID: {result.get('message_id')}")
        print(f"   Cost: {result.get('cost')}")
    else:
        print("❌ SMS failed!")
        print(f"   Error: {result.get('error')}")
    
    return result

def test_notification_manager_with_logging():
    """Test notification manager with logging"""
    print("\n" + "=" * 50)
    print("📱 Testing Notification Manager with Logging")
    print("=" * 50)
    
    try:
        # Get a customer
        customer = Customer.objects.get(email="john.doe@example.com")
        print(f"Testing with customer: {customer.full_name}")
        
        # Test custom notification
        notification_manager = NotificationManager()
        result = notification_manager.send_custom_notification(
            customer=customer,
            message="Test notification from OrderFlow notification manager with logging!",
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

def test_order_notification_with_logging():
    """Test order notification with logging"""
    print("\n" + "=" * 50)
    print("📦 Testing Order Notification with Logging")
    print("=" * 50)
    
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

def check_log_files():
    """Check log files for entries"""
    print("\n" + "=" * 50)
    print("📋 Checking Log Files")
    print("=" * 50)
    
    log_files = [
        'logs/sms.log',
        'logs/orderflow.log',
        'logs/error.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 {log_file}:")
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   Total lines: {len(lines)}")
                        print("   Last 5 entries:")
                        for line in lines[-5:]:
                            print(f"   {line.strip()}")
                    else:
                        print("   File is empty")
            except Exception as e:
                print(f"   Error reading file: {e}")
        else:
            print(f"\n📄 {log_file}: File does not exist")

def main():
    """Run all tests with logging"""
    print("🚀 Starting Comprehensive SMS Testing with Logging")
    print("=" * 60)
    
    # Run tests
    sms_result = test_sms_with_logging()
    manager_result = test_notification_manager_with_logging()
    order_result = test_order_notification_with_logging()
    
    # Wait a moment for logs to be written
    time.sleep(1)
    
    # Check log files
    check_log_files()
    
    print("\n" + "=" * 60)
    print("🎉 SMS Testing with Logging Completed!")
    
    # Summary
    print("\n📊 Test Summary:")
    print(f"   - Direct SMS Service: {'✅ Passed' if sms_result and sms_result.get('success') else '❌ Failed'}")
    print(f"   - Notification Manager: {'✅ Passed' if manager_result and manager_result.get('success') else '❌ Failed'}")
    print(f"   - Order Notification: {'✅ Passed' if order_result and order_result.get('success') else '❌ Failed'}")
    
    print("\n📝 Log Files Created:")
    print("   - logs/sms.log: SMS-specific activities")
    print("   - logs/orderflow.log: General application logs")
    print("   - logs/error.log: Error logs only")
    
    print("\n🔧 To view logs in real-time:")
    print("   - Windows: Get-Content logs/sms.log -Wait")
    print("   - Linux/Mac: tail -f logs/sms.log")

if __name__ == "__main__":
    main()
