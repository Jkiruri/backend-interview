#!/usr/bin/env python3
"""
Simple test to verify Celery is working
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from orderflow.celery import debug_task

def test_simple_celery():
    """Test simple Celery task"""
    print("🔧 Testing Simple Celery Task")
    print("=" * 40)
    
    try:
        # Send a simple task
        result = debug_task.delay()
        print(f"Task ID: {result.id}")
        print(f"Task Status: {result.status}")
        
        # Wait for result
        try:
            task_result = result.get(timeout=10)
            print(f"Task Result: {task_result}")
            print("✅ Celery is working!")
        except Exception as e:
            print(f"⚠️  Task timeout: {e}")
            print("💡 Make sure Celery worker is running!")
            
    except Exception as e:
        print(f"❌ Celery error: {e}")

if __name__ == "__main__":
    test_simple_celery()
