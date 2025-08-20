#!/usr/bin/env python3
"""
Comprehensive test script for OrderFlow notifications
This script tests the entire notification pipeline
"""
import os
import django
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from orders.models import Order, OrderItem
from products.models import Product
from customers.models import Customer
from notifications.tasks import send_order_confirmation, send_admin_order_notification, send_email_notification
from notifications.models import Notification
from notifications.email_service import EmailService
from django.core.mail import send_mail
from django.conf import settings
from celery import current_app

def test_email_configuration():
    """Test email configuration"""
    print("=" * 60)
    print("📧 TESTING EMAIL CONFIGURATION")
    print("=" * 60)
    
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'NOT SET')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
    print(f"EMAIL_HOST_PASSWORD: {'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NOT SET'}")
    
    # Test direct email sending
    try:
        result = send_mail(
            'Test Email from OrderFlow',
            'This is a test email to verify the email configuration is working.',
            'noreply@jameskiruri.co.ke',
            ['test@example.com'],  # This will fail but we can see the error
            fail_silently=True
        )
        print(f"✅ Direct email test result: {result}")
    except Exception as e:
        print(f"❌ Direct email test failed: {e}")

def test_celery_connection():
    """Test Celery connection and workers"""
    print("\n" + "=" * 60)
    print("🔧 TESTING CELERY CONNECTION")
    print("=" * 60)
    
    try:
        # Test Celery connection
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        registered_workers = inspect.registered()
        
        print(f"✅ Celery connection successful")
        print(f"Active workers: {len(active_workers) if active_workers else 0}")
        print(f"Registered workers: {len(registered_workers) if registered_workers else 0}")
        
        if registered_workers:
            for worker, tasks in registered_workers.items():
                print(f"  Worker {worker}: {len(tasks)} tasks")
        
    except Exception as e:
        print(f"❌ Celery connection failed: {e}")

def test_email_service():
    """Test email service"""
    print("\n" + "=" * 60)
    print("📧 TESTING EMAIL SERVICE")
    print("=" * 60)
    
    try:
        email_service = EmailService()
        result = email_service.send_email(
            to_email='jamesnjunge45@gmail.com',
            subject='Test Email Service',
            message='This is a test email from the EmailService class.'
        )
        print(f"✅ Email service test result: {result}")
    except Exception as e:
        print(f"❌ Email service test failed: {e}")

def test_task_queuing():
    """Test task queuing"""
    print("\n" + "=" * 60)
    print("📋 TESTING TASK QUEUING")
    print("=" * 60)
    
    # Get test data
    customer = Customer.objects.first()
    product = Product.objects.first()
    
    if not customer:
        print("❌ No customer found for testing")
        return
    
    if not product:
        print("❌ No product found for testing")
        return
    
    print(f"Testing with customer: {customer.email}")
    print(f"Testing with product: {product.name}")
    
    # Create a test order
    try:
        order = Order.objects.create(
            customer=customer,
            shipping_address="Test Address for Notifications",
            billing_address="Test Billing Address",
            total_amount=product.price * 2,
            status='pending'
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=2,
            unit_price=product.price,
            subtotal=product.price * 2
        )
        
        print(f"✅ Test order created: {order.order_number}")
        
        # Test task queuing
        print("\n🔍 Queueing notification tasks...")
        
        # Queue customer notification
        customer_task = send_order_confirmation.delay(
            str(order.id), 
            send_sms=True, 
            send_email=True
        )
        print(f"✅ Customer task queued: {customer_task.id}")
        
        # Queue admin notification
        admin_task = send_admin_order_notification.delay(str(order.id))
        print(f"✅ Admin task queued: {admin_task.id}")
        
        # Check task status
        print("\n🔍 Checking task status...")
        time.sleep(3)
        
        print(f"Customer task status: {customer_task.status}")
        print(f"Admin task status: {admin_task.status}")
        
        if customer_task.ready():
            print(f"Customer task result: {customer_task.result}")
        
        if admin_task.ready():
            print(f"Admin task result: {admin_task.result}")
        
        return order
        
    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        return None

def test_notification_creation():
    """Test notification creation"""
    print("\n" + "=" * 60)
    print("📢 TESTING NOTIFICATION CREATION")
    print("=" * 60)
    
    customer = Customer.objects.first()
    if not customer:
        print("❌ No customer found for testing")
        return
    
    try:
        # Create a test notification
        notification = Notification.objects.create(
            notification_type='email',
            recipient=customer,
            subject='Test Notification',
            message='This is a test notification to verify the system is working.',
            status='pending'
        )
        
        print(f"✅ Test notification created: {notification.id}")
        
        # Test email notification task
        result = send_email_notification.delay(str(notification.id))
        print(f"✅ Email notification task queued: {result.id}")
        
        # Check task status
        time.sleep(3)
        print(f"Task status: {result.status}")
        
        if result.ready():
            print(f"Task result: {result.result}")
        
        return notification
        
    except Exception as e:
        print(f"❌ Error creating test notification: {e}")
        return None

def check_rabbitmq_queues():
    """Check RabbitMQ queues"""
    print("\n" + "=" * 60)
    print("🐰 CHECKING RABBITMQ QUEUES")
    print("=" * 60)
    
    try:
        # This would require rabbitmqctl command
        print("To check RabbitMQ queues, run:")
        print("docker compose exec rabbitmq rabbitmqctl list_queues name messages consumers")
        print("\nOr visit: https://rabbitmq.orderflow.jameskiruri.co.ke/#/queues")
    except Exception as e:
        print(f"❌ Error checking RabbitMQ: {e}")

def main():
    """Run all tests"""
    print("🚀 ORDERFLOW NOTIFICATION SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Email Configuration
    test_email_configuration()
    
    # Test 2: Celery Connection
    test_celery_connection()
    
    # Test 3: Email Service
    test_email_service()
    
    # Test 4: Task Queuing
    order = test_task_queuing()
    
    # Test 5: Notification Creation
    notification = test_notification_creation()
    
    # Test 6: RabbitMQ Check
    check_rabbitmq_queues()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if order:
        print(f"✅ Test order created: {order.order_number}")
    else:
        print("❌ Test order creation failed")
    
    if notification:
        print(f"✅ Test notification created: {notification.id}")
    else:
        print("❌ Test notification creation failed")
    
    print("\n🔍 Next steps:")
    print("1. Check Celery worker logs: docker compose logs celery_email_worker")
    print("2. Check RabbitMQ queues: https://rabbitmq.orderflow.jameskiruri.co.ke/#/queues")
    print("3. Check Flower monitoring: https://monitor.orderflow.jameskiruri.co.ke/")
    print("4. Check Django logs: docker compose logs web")

if __name__ == "__main__":
    main()
