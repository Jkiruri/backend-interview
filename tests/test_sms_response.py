#!/usr/bin/env python
"""
Test SMS response structure
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.conf import settings
import africastalking

def test_sms_response():
    """Test SMS response structure"""
    print("🔍 Testing SMS Response Structure")
    print("=" * 40)
    
    try:
        # Initialize SMS service
        sms = africastalking.SMSService(settings.AFRICASTALKING_USERNAME, settings.AFRICASTALKING_API_KEY)
        
        # Test phone number (replace with your actual phone number)
        test_phone = "+254700123456"  # Replace with your phone number
        test_message = "Test SMS from OrderFlow"
        
        print(f"Sending to: {test_phone}")
        print(f"Message: {test_message}")
        
        # Send SMS and capture response
        response = sms.send(test_message, [test_phone], sender_id=settings.AFRICASTALKING_SENDER_ID)
        
        print(f"\nResponse type: {type(response)}")
        print(f"Response: {response}")
        
        if isinstance(response, dict):
            print("\nResponse keys:")
            for key in response.keys():
                print(f"  - {key}: {response[key]}")
        
        # Try to access the response safely
        if isinstance(response, dict) and 'SMSMessageData' in response:
            sms_data = response['SMSMessageData']
            print(f"\nSMSMessageData: {sms_data}")
            
            if 'Recipients' in sms_data:
                recipients = sms_data['Recipients']
                print(f"Recipients: {recipients}")
                print(f"Recipients length: {len(recipients)}")
                
                if len(recipients) > 0:
                    first_recipient = recipients[0]
                    print(f"First recipient: {first_recipient}")
                else:
                    print("No recipients in response")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_response()
