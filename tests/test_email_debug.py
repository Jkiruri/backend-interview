#!/usr/bin/env python3
"""
Email debugging test for OrderFlow
Tests email configuration and identifies issues
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail, get_connection
from notifications.email_service import EmailService
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email_settings():
    """Test email settings configuration"""
    print("=" * 60)
    print("📧 EMAIL SETTINGS DEBUG")
    print("=" * 60)
    
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'NOT SET')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    print(f"EMAIL_HOST_PASSWORD: {'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NOT SET'}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
    
    # Check if settings are complete
    required_settings = ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']
    missing_settings = []
    
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(setting)
    
    if missing_settings:
        print(f"\n❌ Missing email settings: {missing_settings}")
        return False
    else:
        print("\n✅ All required email settings are configured")
        return True

def test_smtp_connection():
    """Test SMTP connection directly"""
    print("\n" + "=" * 60)
    print("🔌 SMTP CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Test connection
        if settings.EMAIL_USE_SSL:
            print("Testing SSL connection...")
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        else:
            print("Testing regular connection...")
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if settings.EMAIL_USE_TLS:
                print("Starting TLS...")
                server.starttls()
        
        print("Attempting login...")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("✅ SMTP connection and authentication successful!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication failed: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"❌ SMTP Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        return False

def test_django_email():
    """Test Django's email sending"""
    print("\n" + "=" * 60)
    print("🐍 DJANGO EMAIL TEST")
    print("=" * 60)
    
    try:
        # Test with a real email address
        result = send_mail(
            subject='Test Email from OrderFlow - Django Test',
            message='This is a test email to verify Django email configuration is working.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['jamesnjunge45@gmail.com'],  # Use a real email
            fail_silently=False
        )
        
        print(f"✅ Django email test result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Django email test failed: {e}")
        return False

def test_email_service():
    """Test EmailService class"""
    print("\n" + "=" * 60)
    print("📧 EMAIL SERVICE TEST")
    print("=" * 60)
    
    try:
        email_service = EmailService()
        result = email_service.send_email(
            to_email='jamesnjunge45@gmail.com',
            subject='Test Email from OrderFlow - EmailService Test',
            message='This is a test email to verify the EmailService class is working.'
        )
        
        print(f"✅ EmailService test result: {result}")
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ EmailService test failed: {e}")
        return False

def test_admin_notification():
    """Test admin notification specifically"""
    print("\n" + "=" * 60)
    print("👤 ADMIN NOTIFICATION TEST")
    print("=" * 60)
    
    try:
        from notifications.admin_service import AdminService
        from customers.models import Admin, Customer
        
        # Find the admin user
        admin = Admin.objects.filter(user__email='njungekiruri@gmail.com').first()
        
        if not admin:
            print("❌ Admin user 'njungekiruri@gmail.com' not found")
            return False
        
        print(f"✅ Found admin: {admin.user.email} (Role: {admin.role})")
        print(f"Admin active: {admin.is_active}")
        print(f"User active: {admin.user.is_active}")
        
        # Test admin notification
        admin_service = AdminService()
        result = admin_service.send_admin_notification(
            subject='Test Admin Notification',
            message='This is a test admin notification to verify the system is working.',
            notification_type='test'
        )
        
        print(f"✅ Admin notification test result: {result}")
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Admin notification test failed: {e}")
        return False

def main():
    """Run all email tests"""
    print("🚀 ORDERFLOW EMAIL DEBUGGING TEST")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Email Settings
    results['settings'] = test_email_settings()
    
    # Test 2: SMTP Connection
    if results['settings']:
        results['smtp'] = test_smtp_connection()
    else:
        print("\n⚠️  Skipping SMTP test due to missing settings")
        results['smtp'] = False
    
    # Test 3: Django Email
    if results['smtp']:
        results['django'] = test_django_email()
    else:
        print("\n⚠️  Skipping Django email test due to SMTP failure")
        results['django'] = False
    
    # Test 4: Email Service
    if results['django']:
        results['email_service'] = test_email_service()
    else:
        print("\n⚠️  Skipping EmailService test due to Django email failure")
        results['email_service'] = False
    
    # Test 5: Admin Notification
    if results['email_service']:
        results['admin_notification'] = test_admin_notification()
    else:
        print("\n⚠️  Skipping admin notification test due to EmailService failure")
        results['admin_notification'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EMAIL DEBUG RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All email tests passed! Email system is working.")
    else:
        print("🔧 Email issues detected. Check the output above for details.")
        
        # Provide troubleshooting tips
        print("\n🔍 TROUBLESHOOTING TIPS:")
        if not results['settings']:
            print("- Check your .env file for missing email settings")
        if not results['smtp']:
            print("- Verify SMTP credentials and server settings")
            print("- Check if your email provider allows SMTP access")
        if not results['django']:
            print("- Django email configuration issue")
        if not results['email_service']:
            print("- EmailService class issue")
        if not results['admin_notification']:
            print("- Admin notification system issue")

if __name__ == "__main__":
    main()
