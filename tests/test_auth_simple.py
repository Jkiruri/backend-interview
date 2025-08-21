#!/usr/bin/env python
"""
Simple authentication test
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """Test customer login"""
    print("🚀 Testing Customer Login")
    print("=" * 50)
    
    login_data = {
        "email": "john.doe@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Token: {data.get('token')[:20]}...")
            print(f"Customer: {data.get('customer', {}).get('full_name')}")
            return data.get('token')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    test_login()






