#!/usr/bin/env python
"""
Debug script to check URL patterns
"""
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.urls import reverse
from rest_framework.test import APIRequestFactory
from products.views import CategoryViewSet

def debug_urls():
    """Debug URL patterns"""
    print("🔍 Debugging URL Patterns...")
    print("=" * 50)
    
    # Create a request factory
    factory = APIRequestFactory()
    
    # Create a viewset instance
    viewset = CategoryViewSet()
    
    # Get the URL patterns
    print("\n1. Checking ViewSet actions...")
    print(f"   ViewSet class: {CategoryViewSet.__name__}")
    print(f"   Actions: {[action for action in dir(viewset) if not action.startswith('_')]}")
    
    # Check if the actions are properly decorated
    print("\n2. Checking action decorators...")
    average_price_action = getattr(viewset, 'average_price', None)
    if average_price_action:
        print(f"   average_price action exists: {average_price_action}")
        print(f"   average_price action type: {type(average_price_action)}")
    else:
        print("   ❌ average_price action not found!")
    
    average_price_per_category_action = getattr(viewset, 'average_price_per_category', None)
    if average_price_per_category_action:
        print(f"   average_price_per_category action exists: {average_price_per_category_action}")
        print(f"   average_price_per_category action type: {type(average_price_per_category_action)}")
    else:
        print("   ❌ average_price_per_category action not found!")
    
    # Try to get the URL patterns
    print("\n3. Checking URL patterns...")
    try:
        from orderflow.urls import router
        print(f"   Router: {router}")
        print(f"   Router URLs: {router.urls}")
        
        # Look for category URLs
        category_urls = [url for url in router.urls if 'categories' in str(url.pattern)]
        print(f"   Category URLs found: {len(category_urls)}")
        for url in category_urls:
            print(f"     - {url.pattern}")
    except Exception as e:
        print(f"   ❌ Error getting URL patterns: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 URL debugging completed!")

if __name__ == "__main__":
    debug_urls()
