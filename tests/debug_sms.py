#!/usr/bin/env python
"""
Debug script for Africa's Talking SMS initialization
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.conf import settings
import africastalking

def debug_sms():
    """Debug SMS service initialization"""
    print("🔍 Debugging Africa's Talking SMS Initialization")
    print("=" * 50)
    
    # Check configuration
    print(f"Username: {settings.AFRICASTALKING_USERNAME}")
    print(f"API Key: {settings.AFRICASTALKING_API_KEY[:20]}...")
    print(f"Sender ID: {settings.AFRICASTALKING_SENDER_ID}")
    print()
    
    # Test direct initialization
    try:
        print("Testing direct africastalking.SMS initialization...")
        sms = africastalking.SMS(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
        print("✅ SMS object created successfully!")
        print(f"SMS object type: {type(sms)}")
        print(f"SMS object: {sms}")
        
        # Test sending a simple message
        print("\nTesting SMS send method...")
        test_phone = "+254700123456"  # Replace with your phone number
        test_message = "Test SMS from OrderFlow"
        
        print(f"Sending to: {test_phone}")
        print(f"Message: {test_message}")
        
        response = sms.send(test_message, [test_phone], sender=settings.AFRICASTALKING_SENDER_ID)
        print(f"✅ SMS sent successfully!")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_sms()
