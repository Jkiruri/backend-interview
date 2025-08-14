#!/usr/bin/env python
"""
Simple test script for Africa's Talking SMS functionality
"""
import os
import django

# Setup Django
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from notifications.sms_service import SMSService
from django.conf import settings

def test_sms():
    """Test SMS service directly"""
    print("🚀 Testing Africa's Talking SMS Integration")
    print("=" * 50)
    
    # Check configuration
    print(f"Username: {settings.AFRICASTALKING_USERNAME}")
    print(f"API Key: {settings.AFRICASTALKING_API_KEY[:20]}...")
    print(f"Sender ID: {settings.AFRICASTALKING_SENDER_ID}")
    print()
    
    # Initialize SMS service
    sms_service = SMSService()
    
    # TODO: Replace with your actual phone number
    test_phone = "+254700123456"  # Replace this with your phone number
    test_message = "Hello from OrderFlow! This is a test SMS from Africa's Talking."
    
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
        
        print("\n🔧 Troubleshooting:")
        print("   - Make sure you replaced the phone number with your actual number")
        print("   - Check Africa's Talking account has sufficient credits")
        print("   - Verify the API key and username are correct")
        print("   - If using sandbox, make sure the phone number is registered")
    
    return result

if __name__ == "__main__":
    test_sms()
