#!/usr/bin/env python
"""
Direct endpoint test
"""
import requests

BASE_URL = "http://localhost:8000"

def test_direct_endpoints():
    """Test endpoints directly"""
    print("🧪 Testing Direct Endpoints...")
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
    
    # Test categories list
    print("\n2. Testing categories list...")
    response = requests.get(f"{BASE_URL}/api/v1/categories/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data.get('results', []))} categories")
    
    # Test average price endpoint
    print("\n3. Testing average price endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/categories/average-price/?slug=electronics", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    # Test average price per category endpoint
    print("\n4. Testing average price per category endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/categories/average-price-per-category/", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
    
    # Test tree endpoint
    print("\n5. Testing tree endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/categories/tree/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} root categories")

if __name__ == "__main__":
    test_direct_endpoints()
