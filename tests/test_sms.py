#!/usr/bin/env python3
"""
Test script for SMS functionality using Africa's Talking API
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from notifications.sms_service import SMSService
from customers.models import Customer
from django.conf import settings

def test_sms_configuration():
    """Test SMS configuration"""
    print("=" * 60)
    print("📱 TESTING SMS CONFIGURATION")
    print("=" * 60)
    
    print(f"AFRICASTALKING_API_KEY: {'SET' if getattr(settings, 'AFRICASTALKING_API_KEY', None) else 'NOT SET'}")
    print(f"AFRICASTALKING_USERNAME: {getattr(settings, 'AFRICASTALKING_USERNAME', 'NOT SET')}")
    print(f"AFRICAS_TALKING_SANDBOX: {getattr(settings, 'AFRICAS_TALKING_SANDBOX', 'NOT SET')}")

def test_sms_service():
    """Test SMS service"""
    print("\n" + "=" * 60)
    print("📱 TESTING SMS SERVICE")
    print("=" * 60)
    
    try:
        sms_service = SMSService()
        
        # Get a customer with phone number
        customer = Customer.objects.filter(phone_number__isnull=False).exclude(phone_number='').first()
        
        if customer:
            print(f"Testing with customer: {customer.email}")
            print(f"Phone number: {customer.phone_number}")
            
            # Test SMS sending
            result = sms_service.send_sms(
                phone_number=customer.phone_number,
                message="Test SMS from OrderFlow - Your order has been confirmed!",
                notification_id="test-123"
            )
            
            print(f"✅ SMS test result: {result}")
        else:
            print("❌ No customer with phone number found for testing")
            
    except Exception as e:
        print(f"❌ SMS service test failed: {e}")

def test_order_sms():
    """Test order SMS notification"""
    print("\n" + "=" * 60)
    print("📱 TESTING ORDER SMS NOTIFICATION")
    print("=" * 60)
    
    try:
        from orders.models import Order
        
        # Get the latest order
        order = Order.objects.last()
        
        if order:
            print(f"Testing with order: {order.order_number}")
            
            sms_service = SMSService()
            result = sms_service.send_order_confirmation(order)
            
            print(f"✅ Order SMS result: {result}")
        else:
            print("❌ No orders found for testing")
            
    except Exception as e:
        print(f"❌ Order SMS test failed: {e}")

def main():
    """Run all SMS tests"""
    print("🚀 ORDERFLOW SMS SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: SMS Configuration
    test_sms_configuration()
    
    # Test 2: SMS Service
    test_sms_service()
    
    # Test 3: Order SMS
    test_order_sms()
    
    print("\n" + "=" * 60)
    print("📊 SMS TEST SUMMARY")
    print("=" * 60)
    print("✅ SMS tests completed")
    print("\n🔍 Next steps:")
    print("1. Check SMS delivery in Africa's Talking dashboard")
    print("2. Verify phone numbers are in correct format (+254...)")
    print("3. Check SMS worker logs: docker compose logs celery_sms_worker")

if __name__ == "__main__":
    main()
