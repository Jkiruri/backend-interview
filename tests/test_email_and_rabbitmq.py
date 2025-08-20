#!/usr/bin/env python3
"""
Test script to verify email functionality and RabbitMQ setup
"""
import os
import django
import requests
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from notifications.email_service import EmailService
from notifications.sms_service import SMSService
from notifications.tasks import send_email_notification, send_sms_notification
from orders.models import Order
from customers.models import Customer
from celery import current_app

def test_email_configuration():
    """Test email configuration"""
    print("=" * 60)
    print("📧 TESTING EMAIL CONFIGURATION")
    print("=" * 60)
    
    try:
        # Test basic email sending
        print(f"Email Host: {settings.EMAIL_HOST}")
        print(f"Email Port: {settings.EMAIL_PORT}")
        print(f"Email User: {settings.EMAIL_HOST_USER}")
        print(f"SSL Enabled: {settings.EMAIL_USE_SSL}")
        
        # Test sending a simple email
        result = send_mail(
            subject='OrderFlow Test Email',
            message='This is a test email from OrderFlow system.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['james@jameskiruri.co.ke'],  # Your email address
            fail_silently=False
        )
        
        if result:
            print("✅ Basic email sending works!")
        else:
            print("❌ Basic email sending failed")
            
    except Exception as e:
        print(f"❌ Email configuration error: {e}")

def test_email_service():
    """Test the email service"""
    print("\n" + "=" * 60)
    print("📧 TESTING EMAIL SERVICE")
    print("=" * 60)
    
    try:
        email_service = EmailService()
        
        # Test email service initialization
        print(f"From Email: {email_service.from_email}")
        print(f"Fail Silently: {email_service.fail_silently}")
        
        # Test sending email through service
        result = email_service.send_email(
            to_email='james@jameskiruri.co.ke',  # Your email address
            subject='OrderFlow Email Service Test',
            message='This is a test email from OrderFlow Email Service.',
            html_message='<h1>OrderFlow Test</h1><p>This is a test email from OrderFlow Email Service.</p>'
        )
        
        print(f"Email Service Result: {result}")
        
        if result.get('success'):
            print("✅ Email service works!")
        else:
            print(f"❌ Email service failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Email service error: {e}")

def test_rabbitmq_connection():
    """Test RabbitMQ connection"""
    print("\n" + "=" * 60)
    print("🐰 TESTING RABBITMQ CONNECTION")
    print("=" * 60)
    
    try:
        # Test Celery broker connection
        print(f"Celery Broker URL: {settings.CELERY_BROKER_URL}")
        print(f"Celery Result Backend: {settings.CELERY_RESULT_BACKEND}")
        
        # Test Celery app configuration
        app = current_app
        print(f"Celery App: {app}")
        
        # Test broker connection
        with app.connection() as conn:
            print("✅ RabbitMQ connection successful!")
            
        # Test queue inspection
        inspector = app.control.inspect()
        stats = inspector.stats()
        
        if stats:
            print("✅ Celery workers are running!")
            for worker, info in stats.items():
                print(f"  - Worker: {worker}")
        else:
            print("⚠️  No Celery workers found (this is normal if workers aren't running)")
            
    except Exception as e:
        print(f"❌ RabbitMQ connection error: {e}")

def test_celery_tasks():
    """Test Celery tasks"""
    print("\n" + "=" * 60)
    print("🔧 TESTING CELERY TASKS")
    print("=" * 60)
    
    try:
        # Test task registration
        app = current_app
        registered_tasks = app.tasks.keys()
        
        print("Registered Celery tasks:")
        for task in registered_tasks:
            if 'notifications' in task:
                print(f"  - {task}")
        
        # Test simple task execution
        from orderflow.celery import debug_task
        result = debug_task.delay()
        
        print(f"Debug task ID: {result.id}")
        print(f"Debug task status: {result.status}")
        
        # Wait for result
        try:
            task_result = result.get(timeout=10)
            print(f"Debug task result: {task_result}")
            print("✅ Celery task execution works!")
        except Exception as e:
            print(f"⚠️  Task execution timeout or error: {e}")
            
    except Exception as e:
        print(f"❌ Celery task error: {e}")

def test_order_confirmation_email():
    """Test order confirmation email"""
    print("\n" + "=" * 60)
    print("📋 TESTING ORDER CONFIRMATION EMAIL")
    print("=" * 60)
    
    try:
        # Get or create a test order
        customer, created = Customer.objects.get_or_create(
            email='james@jameskiruri.co.ke',
            defaults={
                'first_name': 'James',
                'last_name': 'Kiruri',
                'phone_number': '+254700000000',
                'is_verified': True,
                'is_active': True
            }
        )
        
        if created:
            customer.set_password('testpassword123')
            customer.save()
            print(f"✅ Created test customer: {customer.email}")
        
        # Get first order or create one
        order = Order.objects.first()
        if not order:
            print("❌ No orders found in database. Please create an order first.")
            return
        
        print(f"Testing with order: {order.order_number}")
        
        # Test email service order confirmation
        email_service = EmailService()
        result = email_service.send_order_confirmation(order)
        
        print(f"Order confirmation email result: {result}")
        
        if result.get('success'):
            print("✅ Order confirmation email works!")
        else:
            print(f"❌ Order confirmation email failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Order confirmation email error: {e}")

def test_sms_service():
    """Test SMS service"""
    print("\n" + "=" * 60)
    print("📱 TESTING SMS SERVICE")
    print("=" * 60)
    
    try:
        sms_service = SMSService()
        
        print(f"Africa's Talking Username: {sms_service.username}")
        print(f"Africa's Talking API Key: {sms_service.api_key[:20]}...")
        print(f"Sender ID: {sms_service.sender_id}")
        
        # Test SMS service initialization
        if sms_service.sms:
            print("✅ SMS service initialized successfully!")
        else:
            print("❌ SMS service initialization failed")
            
    except Exception as e:
        print(f"❌ SMS service error: {e}")

def test_notification_tasks():
    """Test notification tasks"""
    print("\n" + "=" * 60)
    print("🔔 TESTING NOTIFICATION TASKS")
    print("=" * 60)
    
    try:
        # Test order confirmation task
        order = Order.objects.first()
        if order:
            print(f"Testing notification tasks with order: {order.order_number}")
            
            # Test order confirmation task
            from notifications.tasks import send_order_confirmation
            result = send_order_confirmation.delay(str(order.id), send_sms=False, send_email=True)
            
            print(f"Order confirmation task ID: {result.id}")
            print(f"Order confirmation task status: {result.status}")
            
            # Wait for result
            try:
                task_result = result.get(timeout=30)
                print(f"Order confirmation task result: {task_result}")
                print("✅ Notification tasks work!")
            except Exception as e:
                print(f"⚠️  Task execution timeout or error: {e}")
        else:
            print("❌ No orders found to test notification tasks")
            
    except Exception as e:
        print(f"❌ Notification tasks error: {e}")

def main():
    """Run all tests"""
    print("🚀 ORDERFLOW EMAIL & RABBITMQ TEST SUITE")
    print("=" * 60)
    
    # Test email configuration
    test_email_configuration()
    
    # Test email service
    test_email_service()
    
    # Test RabbitMQ connection
    test_rabbitmq_connection()
    
    # Test Celery tasks
    test_celery_tasks()
    
    # Test order confirmation email
    test_order_confirmation_email()
    
    # Test SMS service
    test_sms_service()
    
    # Test notification tasks
    test_notification_tasks()
    
    print("\n" + "=" * 60)
    print("🏁 TEST SUITE COMPLETED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start Celery workers: celery -A orderflow worker -l info")
    print("2. Start Celery Beat: celery -A orderflow beat -l info")
    print("3. Monitor tasks: celery -A orderflow flower")
    print("4. Check RabbitMQ Management: http://localhost:15672")

if __name__ == "__main__":
    main()
