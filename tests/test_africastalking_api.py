#!/usr/bin/env python
"""
Test Africa's Talking API
"""
import africastalking

def test_api():
    """Test Africa's Talking API"""
    print("🔍 Testing Africa's Talking API")
    print("=" * 40)
    
    # Check SMSService
    print("SMSService methods:")
    sms_service = africastalking.SMSService("test", "test")
    
    # Get the send method
    send_method = getattr(sms_service, 'send', None)
    if send_method:
        import inspect
        sig = inspect.signature(send_method)
        print(f"send method signature: {sig}")
        print(f"send method doc: {send_method.__doc__}")
    else:
        print("No send method found")
    
    # Check if there's a different method
    methods = [m for m in dir(sms_service) if not m.startswith('_')]
    print(f"Available methods: {methods}")

if __name__ == "__main__":
    test_api()
