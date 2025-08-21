#!/usr/bin/env python
"""
Test different URL variations
"""
import requests

BASE_URL = "http://localhost:8000"

def test_url_variations():
    """Test different URL variations"""
    print("🧪 Testing URL Variations...")
    print("=" * 50)
    
    # Get token
    print("\n1. Getting token...")
    login_data = {
        "email": "admin@jameskiruri.co.ke",
        "password": "admin123456"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login/",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return
    
    token = response.json().get('token')
    headers = {"Authorization": f"Token {token}"}
    print(f"✅ Token: {token[:20]}...")
    
    # Test different URL variations for average_price
    print("\n2. Testing average_price URL variations...")
    urls_to_test = [
        "/api/v1/categories/average-price/",
        "/api/v1/categories/average-price",
        "/api/v1/categories/average-price/?slug=electronics",
        "/api/v1/categories/average-price?slug=electronics",
    ]
    
    for url in urls_to_test:
        full_url = BASE_URL + url
        print(f"   Testing: {url}")
        response = requests.get(full_url, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.text[:100]}")
        print()
    
    # Test different URL variations for average_price_per_category
    print("\n3. Testing average_price_per_category URL variations...")
    urls_to_test = [
        "/api/v1/categories/average-price-per-category/",
        "/api/v1/categories/average-price-per-category",
    ]
    
    for url in urls_to_test:
        full_url = BASE_URL + url
        print(f"   Testing: {url}")
        response = requests.get(full_url, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.text[:100]}")
        print()

if __name__ == "__main__":
    test_url_variations()
