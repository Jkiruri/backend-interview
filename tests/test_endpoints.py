#!/usr/bin/env python
"""
Test script to verify API endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test the main API endpoints"""
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    # Test 1: Get all products (public endpoint)
    print("\n1. Testing GET /api/v1/products/")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/products/")
        if response.status_code == 200:
            print("✅ Products endpoint working!")
            products = response.json()
            print(f"   Found {len(products)} products")
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get all categories (public endpoint)
    print("\n2. Testing GET /api/v1/categories/")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/categories/")
        if response.status_code == 200:
            print("✅ Categories endpoint working!")
            categories = response.json()
            print(f"   Found {len(categories)} categories")
        else:
            print(f"❌ Categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test customer registration
    print("\n3. Testing POST /api/v1/auth/register/")
    try:
        data = {
            "email": "testuser@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+254700123456",
            "address": "123 Test St, Nairobi, Kenya",
            "city": "Nairobi",
            "state": "Nairobi",
            "country": "Kenya",
            "postal_code": "00100"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [201, 400]:  # 400 if user already exists
            print("✅ Registration endpoint working!")
            if response.status_code == 201:
                print("   User created successfully")
            else:
                print("   User already exists (expected)")
        else:
            print(f"❌ Registration endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Test customer login
    print("\n4. Testing POST /api/v1/auth/login/")
    try:
        data = {
            "email": "testuser@example.com",
            "password": "password123"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Login endpoint working!")
            login_data = response.json()
            if 'token' in login_data:
                print("   Token received successfully")
                token = login_data['token']
            else:
                print("   Login successful but no token")
                token = None
        else:
            print(f"❌ Login endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            token = None
    except Exception as e:
        print(f"❌ Error: {e}")
        token = None
    
    # Test 5: Test admin login
    print("\n5. Testing Admin Login")
    try:
        data = {
            "email": "admin@jameskiruri.co.ke",
            "password": "admin123456"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login/",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ Admin login working!")
            admin_data = response.json()
            if 'token' in admin_data:
                print("   Admin token received")
                admin_token = admin_data['token']
            else:
                print("   Admin login successful but no token")
                admin_token = None
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            admin_token = None
    except Exception as e:
        print(f"❌ Error: {e}")
        admin_token = None
    
    # Test 6: Test admin dashboard (if we have admin token)
    if admin_token:
        print("\n6. Testing Admin Dashboard")
        try:
            headers = {"Authorization": f"Token {admin_token}"}
            response = requests.get(
                f"{BASE_URL}/api/v1/admin/dashboard/",
                headers=headers
            )
            if response.status_code == 200:
                print("✅ Admin dashboard working!")
                dashboard_data = response.json()
                print("   Dashboard data received")
            else:
                print(f"❌ Admin dashboard failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Endpoint testing completed!")
    
    if token:
        print(f"\n🔑 Customer Token: {token}")
    if admin_token:
        print(f"👑 Admin Token: {admin_token}")
    
    print("\n📝 Next steps:")
    print("1. Import the Postman collection: OrderFlow_API.postman_collection.json")
    print("2. Set the base_url variable to: http://localhost:8000")
    print("3. Use the tokens above for authenticated requests")
    print("4. Test all endpoints in Postman!")

if __name__ == "__main__":
    test_endpoints()
