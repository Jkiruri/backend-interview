#!/usr/bin/env python
"""
Test SMS without sender ID
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.conf import settings
import africastalking

def test_sms_no_sender():
    """Test SMS without sender ID"""
    print("🔍 Testing SMS without Sender ID")
    print("=" * 40)
    
    try:
        # Initialize SMS service
        sms = africastalking.SMSService(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
        
        # Test phone number (replace with your actual phone number)
        test_phone = "+254700123456"  # Replace with your phone number
        test_message = "Test SMS from OrderFlow (no sender ID)"
        
        print(f"Sending to: {test_phone}")
        print(f"Message: {test_message}")
        
        # Send SMS without sender_id
        response = sms.send(test_message, [test_phone])
        
        print(f"\nResponse type: {type(response)}")
        print(f"Response: {response}")
        
        if isinstance(response, dict):
            print("\nResponse keys:")
            for key in response.keys():
                print(f"  - {key}: {response[key]}")
        
        # Check if it was successful
        if isinstance(response, dict) and 'SMSMessageData' in response:
            sms_data = response['SMSMessageData']
            if 'Message' in sms_data:
                message = sms_data['Message']
                if message == 'Sent to 1/1 Total Cost: KES 1.0000':
                    print("✅ SMS sent successfully!")
                else:
                    print(f"❌ SMS failed: {message}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_no_sender()
