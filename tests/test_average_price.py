#!/usr/bin/env python
"""
Test script to verify the average price endpoint is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_average_price_endpoint():
    """Test the average price endpoint"""
    print("🧪 Testing Average Price Endpoint...")
    print("=" * 50)
    
    # First, get a token by logging in
    print("\n1. Getting authentication token...")
    try:
        login_data = {
            "email": "admin@jameskiruri.co.ke",
            "password": "admin123456"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            token = response.json().get('token')
            print(f"✅ Token received: {token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return
    
    # Test 2: Get all categories first
    print("\n2. Getting all categories...")
    try:
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/categories/", headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories")
            
            if categories:
                # Use the first category for testing
                first_category = categories[0]
                category_slug = first_category.get('slug', 'electronics')
                print(f"   Using category: {first_category.get('name')} (slug: {category_slug})")
            else:
                print("   No categories found, using default 'electronics'")
                category_slug = 'electronics'
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
            category_slug = 'electronics'  # Use default
    except Exception as e:
        print(f"❌ Error getting categories: {e}")
        category_slug = 'electronics'  # Use default
    
    # Test 3: Get average price for specific category
    print(f"\n3. Testing average price for category: {category_slug}")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/categories/{category_slug}/average-price/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Average price endpoint working!")
            print(f"   Category: {data.get('category_name')}")
            print(f"   Average Price: Ksh {data.get('average_price')}")
            print(f"   Product Count: {data.get('product_count')}")
            print(f"   Min Price: Ksh {data.get('min_price')}")
            print(f"   Max Price: Ksh {data.get('max_price')}")
        else:
            print(f"❌ Average price endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get average prices for all categories
    print("\n4. Testing average prices for all categories...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/categories/average-price-per-category/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Average prices for all categories working!")
            print(f"   Found {len(data)} categories with products")
            
            for item in data[:3]:  # Show first 3
                print(f"   - {item.get('category_name')}: Ksh {item.get('average_price')} ({item.get('product_count')} products)")
        else:
            print(f"❌ Average prices for all categories failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Get category tree
    print("\n5. Testing category tree endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/categories/tree/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Category tree endpoint working!")
            print(f"   Found {len(data)} root categories")
        else:
            print(f"❌ Category tree endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Average price endpoint testing completed!")

if __name__ == "__main__":
    test_average_price_endpoint()
