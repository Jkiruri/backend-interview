#!/usr/bin/env python
"""
Script to check Celery worker status and task processing
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from celery import current_app
from celery.result import AsyncResult

def check_celery_status():
    """Check Celery worker status and active tasks"""
    print("🔍 Checking Celery Status...")
    print("=" * 50)
    
    # Check active workers
    try:
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        registered_workers = inspect.registered()
        stats = inspect.stats()
        
        print(f"📊 Celery Workers Status:")
        if active_workers:
            for worker_name, tasks in active_workers.items():
                print(f"   ✅ Worker: {worker_name}")
                print(f"      Active tasks: {len(tasks)}")
        else:
            print("   ❌ No active workers found")
        
        print(f"\n📋 Registered Workers:")
        if registered_workers:
            for worker_name, tasks in registered_workers.items():
                print(f"   ✅ Worker: {worker_name}")
                print(f"      Registered tasks: {len(tasks)}")
        else:
            print("   ❌ No registered workers found")
        
        print(f"\n📈 Worker Statistics:")
        if stats:
            for worker_name, stat in stats.items():
                print(f"   ✅ Worker: {worker_name}")
                print(f"      Pool: {stat.get('pool', {}).get('implementation', 'Unknown')}")
                print(f"      Processed: {stat.get('total', {}).get('processed', 0)} tasks")
        else:
            print("   ❌ No worker statistics available")
            
    except Exception as e:
        print(f"❌ Error checking Celery status: {e}")
    
    print(f"\n🔧 Celery Configuration:")
    print(f"   Broker URL: {current_app.conf.broker_url}")
    print(f"   Result Backend: {current_app.conf.result_backend}")
    print(f"   Task Routes: {current_app.conf.task_routes}")
    
    # Check if we can ping workers
    print(f"\n🏓 Pinging Workers...")
    try:
        ping_result = current_app.control.ping()
        if ping_result:
            print("   ✅ Workers are responding to ping")
            for worker_name, response in ping_result.items():
                print(f"      {worker_name}: {response}")
        else:
            print("   ❌ No workers responding to ping")
    except Exception as e:
        print(f"   ❌ Error pinging workers: {e}")

if __name__ == "__main__":
    check_celery_status()
