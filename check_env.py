#!/usr/bin/env python3
"""
Check environment variables for Celery and notifications
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.conf import settings

def check_environment():
    """Check all required environment variables"""
    print("=" * 60)
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    # Celery settings
    print("\n📋 CELERY SETTINGS:")
    print(f"   Broker URL: {getattr(settings, 'CELERY_BROKER_URL', 'NOT SET')}")
    print(f"   Result Backend: {getattr(settings, 'CELERY_RESULT_BACKEND', 'NOT SET')}")
    
    # Email settings
    print("\n📧 EMAIL SETTINGS:")
    print(f"   Email Host: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    print(f"   Email Port: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    print(f"   Email User: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    print(f"   Email Password: {'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NOT SET'}")
    print(f"   Email TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
    
    # SMS settings
    print("\n📱 SMS SETTINGS:")
    print(f"   Africa's Talking API Key: {'SET' if getattr(settings, 'AFRICASTALKING_API_KEY', None) else 'NOT SET'}")
    print(f"   Africa's Talking Username: {getattr(settings, 'AFRICASTALKING_USERNAME', 'NOT SET')}")
    print(f"   Africa's Talking Sender ID: {getattr(settings, 'AFRICASTALKING_SENDER_ID', 'NOT SET')}")
    
    # Database settings
    print("\n🗄️  DATABASE SETTINGS:")
    print(f"   Database Name: {getattr(settings, 'DB_NAME', 'NOT SET')}")
    print(f"   Database Host: {getattr(settings, 'DB_HOST', 'NOT SET')}")
    print(f"   Database User: {getattr(settings, 'DB_USER', 'NOT SET')}")
    print(f"   Database Password: {'SET' if getattr(settings, 'DB_PASSWORD', None) else 'NOT SET'}")
    
    # Check for missing critical settings
    print("\n⚠️  MISSING CRITICAL SETTINGS:")
    missing = []
    
    if not getattr(settings, 'CELERY_BROKER_URL', None):
        missing.append('CELERY_BROKER_URL')
    
    if not getattr(settings, 'CELERY_RESULT_BACKEND', None):
        missing.append('CELERY_RESULT_BACKEND')
    
    if not getattr(settings, 'EMAIL_HOST_USER', None):
        missing.append('EMAIL_HOST_USER')
    
    if not getattr(settings, 'EMAIL_HOST_PASSWORD', None):
        missing.append('EMAIL_HOST_PASSWORD')
    
    if not getattr(settings, 'AFRICASTALKING_API_KEY', None):
        missing.append('AFRICASTALKING_API_KEY')
    
    if missing:
        for setting in missing:
            print(f"   ❌ {setting}")
    else:
        print("   ✅ All critical settings are configured")
    
    return len(missing) == 0

if __name__ == "__main__":
    all_good = check_environment()
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ Environment check completed - All critical settings are configured!")
    else:
        print("❌ Environment check completed - Some critical settings are missing!")
        print("   Please check your .env file and ensure all required variables are set.")
    print("=" * 60)
