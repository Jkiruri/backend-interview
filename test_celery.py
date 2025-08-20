#!/usr/bin/env python3
"""
Test script to verify Celery workers and queues are working
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from celery import current_app
from notifications.tasks import send_sms_notification, send_email_notification
from orders.tasks import process_order_notification
import time

def test_celery_connection():
    """Test Celery connection and workers"""
    print("=" * 60)
    print("🔧 TESTING CELERY CONNECTION")
    print("=" * 60)
    
    try:
        # Test Celery connection
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        registered_workers = inspect.registered()
        
        print(f"✅ Celery connection successful")
        print(f"📊 Active workers: {len(active_workers) if active_workers else 0}")
        print(f"📋 Registered workers: {len(registered_workers) if registered_workers else 0}")
        
        if active_workers:
            for worker, tasks in active_workers.items():
                print(f"   🔄 {worker}: {len(tasks)} active tasks")
        
        if registered_workers:
            for worker, tasks in registered_workers.items():
                print(f"   📝 {worker}: {len(tasks)} registered tasks")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery connection failed: {e}")
        return False

def test_queue_connection():
    """Test queue connection"""
    print("\n🔍 TESTING QUEUE CONNECTION")
    print("=" * 40)
    
    try:
        # Test broker connection
        broker_url = current_app.conf.broker_url
        print(f"✅ Broker URL: {broker_url}")
        
        # Test result backend
        result_backend = current_app.conf.result_backend
        print(f"✅ Result Backend: {result_backend}")
        
        return True
        
    except Exception as e:
        print(f"❌ Queue connection failed: {e}")
        return False

def test_task_submission():
    """Test submitting tasks to queues"""
    print("\n📤 TESTING TASK SUBMISSION")
    print("=" * 40)
    
    try:
        # Test SMS task
        print("📱 Testing SMS task...")
        sms_result = send_sms_notification.delay(
            phone_number='+254700000001',
            message='Test SMS from OrderFlow',
            order_id='TEST-001'
        )
        print(f"   ✅ SMS task submitted: {sms_result.id}")
        
        # Test Email task
        print("📧 Testing Email task...")
        email_result = send_email_notification.delay(
            email='test@example.com',
            subject='Test Email',
            message='Test email from OrderFlow',
            order_id='TEST-001'
        )
        print(f"   ✅ Email task submitted: {email_result.id}")
        
        # Test Order notification task
        print("📦 Testing Order notification task...")
        order_result = process_order_notification.delay(
            order_id='TEST-001',
            notification_type='order_created'
        )
        print(f"   ✅ Order task submitted: {order_result.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task submission failed: {e}")
        return False

def check_task_status():
    """Check task status after submission"""
    print("\n📊 CHECKING TASK STATUS")
    print("=" * 40)
    
    try:
        # Get recent tasks
        inspect = current_app.control.inspect()
        active_tasks = inspect.active()
        reserved_tasks = inspect.reserved()
        
        if active_tasks:
            print("🔄 Active tasks:")
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    print(f"   - {task['name']} (ID: {task['id']})")
        
        if reserved_tasks:
            print("⏳ Reserved tasks:")
            for worker, tasks in reserved_tasks.items():
                for task in tasks:
                    print(f"   - {task['name']} (ID: {task['id']})")
        
        if not active_tasks and not reserved_tasks:
            print("ℹ️  No active or reserved tasks found")
        
    except Exception as e:
        print(f"❌ Error checking task status: {e}")

if __name__ == "__main__":
    print("🚀 Starting Celery tests...")
    
    # Test connection
    connection_ok = test_celery_connection()
    queue_ok = test_queue_connection()
    
    if connection_ok and queue_ok:
        # Test task submission
        task_ok = test_task_submission()
        
        if task_ok:
            # Wait a moment and check status
            print("\n⏳ Waiting 5 seconds for tasks to process...")
            time.sleep(5)
            check_task_status()
    
    print("\n" + "=" * 60)
    print("✅ Celery testing completed!")
    print("=" * 60)
