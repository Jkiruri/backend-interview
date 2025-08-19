#!/usr/bin/env python
"""
Test Celery configuration and settings loading
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

print("🔧 Testing Celery Configuration...")
print("=" * 50)

# Check Django settings
print(f"📋 Django Settings:")
print(f"   CELERY_BROKER_URL: {getattr(settings, 'CELERY_BROKER_URL', 'Not set')}")
print(f"   CELERY_RESULT_BACKEND: {getattr(settings, 'CELERY_RESULT_BACKEND', 'Not set')}")
print(f"   REDIS_URL: {getattr(settings, 'REDIS_URL', 'Not set')}")

# Import and check Celery app
try:
    from orderflow.celery import app
    print(f"\n✅ Celery app imported successfully")
    print(f"   App name: {app.main}")
    print(f"   Broker URL: {app.conf.broker_url}")
    print(f"   Result Backend: {app.conf.result_backend}")
    print(f"   Task Routes: {app.conf.task_routes}")
    
    # Test task discovery
    print(f"\n📋 Registered Tasks:")
    registered_tasks = app.tasks.keys()
    notification_tasks = [task for task in registered_tasks if 'notifications' in task]
    for task in notification_tasks:
        print(f"   ✅ {task}")
    
    # Test broker connection
    print(f"\n🔌 Testing Broker Connection...")
    try:
        with app.connection() as conn:
            print(f"   ✅ Broker connection successful")
            print(f"   Connection: {conn}")
    except Exception as e:
        print(f"   ❌ Broker connection failed: {e}")
    
except Exception as e:
    print(f"❌ Error importing Celery app: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🎯 Next Steps:")
print(f"   1. Make sure RabbitMQ is running on localhost:5672")
print(f"   2. Make sure Redis is running on localhost:6379")
print(f"   3. Start Celery workers with: celery -A orderflow worker --loglevel=info")
