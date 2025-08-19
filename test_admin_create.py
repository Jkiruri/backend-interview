#!/usr/bin/env python
"""
Test script to verify admin creation endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_admin_create():
    """Test admin creation endpoint"""
    print("🧪 Testing Admin Creation Endpoint...")
    print("=" * 50)
    
    # Step 1: Login as existing admin
    print("\n1. Logging in as existing admin...")
    try:
        admin_login_data = {
            "email": "admin@jameskiruri.co.ke",
            "password": "admin123456"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login/",
            json=admin_login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            admin_token = response.json().get('token')
            print(f"✅ Admin login successful: {admin_token[:20]}...")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error during admin login: {e}")
        return
    
    headers = {"Authorization": f"Token {admin_token}"}
    
    # Step 2: Test admin creation
    print("\n2. Testing admin creation...")
    try:
        new_admin_data = {
            "email": "jamesnjunge45@gmail.com",
            "password": "admin123456",
            "first_name": "New",
            "last_name": "Admin",
            "role": "admin",
            "permissions": ["products", "orders"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/create_admin/",
            json=new_admin_data,
            headers={**headers, "Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin creation successful!")
            print(f"   Email: {new_admin_data['email']}")
            print(f"   Role: {new_admin_data['role']}")
        else:
            print(f"❌ Admin creation failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Admin Creation Test Completed!")

if __name__ == "__main__":
    test_admin_create()
