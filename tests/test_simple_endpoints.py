#!/usr/bin/env python
"""
Simple test script to check if endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    """Test basic endpoints"""
    print("🧪 Testing Basic Endpoints...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/health/")
        if response.status_code == 200:
            print("✅ Server is running!")
        else:
            print(f"❌ Server responded with {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Test 2: Get authentication token
    print("\n2. Getting authentication token...")
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
            headers = {"Authorization": f"Token {token}"}
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return
    
    # Test 3: Get categories with auth
    print("\n3. Testing categories endpoint with auth...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data.get('results', []))} categories")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Test average price endpoint with auth
    print("\n4. Testing average price endpoint with auth...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories/average-price/?slug=electronics", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Average price: {data.get('average_price')}")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Test average price per category endpoint with auth
    print("\n5. Testing average price per category endpoint with auth...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories/average-price-per-category/", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data)} categories with average prices")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Basic endpoint testing completed!")

if __name__ == "__main__":
    test_basic_endpoints()
