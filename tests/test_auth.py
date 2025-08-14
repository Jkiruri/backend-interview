#!/usr/bin/env python
"""
Test script for OIDC and Google OAuth2 authentication
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_traditional_auth():
    """Test traditional email/password authentication"""
    print("=== Testing Traditional Authentication ===")
    
    # Register a new user
    register_data = {
        "email": "test@example.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    print(f"Register: {response.status_code}")
    if response.status_code == 201:
        print("✅ Registration successful")
    else:
        print(f"❌ Registration failed: {response.text}")
    
    # Login
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful")
        token = response.json().get('token')
        return token
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_oidc_endpoints():
    """Test OIDC endpoints"""
    print("\n=== Testing OIDC Endpoints ===")
    
    # Test OIDC login (should redirect)
    response = requests.get(f"{BASE_URL}/auth/oidc/login/", allow_redirects=False)
    print(f"OIDC Login: {response.status_code}")
    if response.status_code == 302:
        print("✅ OIDC login redirects correctly")
    else:
        print(f"❌ OIDC login failed: {response.status_code}")
    
    # Test OIDC token endpoint (should fail without valid tokens)
    response = requests.post(f"{BASE_URL}/auth/oidc/token/", json={})
    print(f"OIDC Token (no data): {response.status_code}")
    if response.status_code == 400:
        print("✅ OIDC token endpoint validates input")

def test_google_oauth_endpoints():
    """Test Google OAuth2 endpoints"""
    print("\n=== Testing Google OAuth2 Endpoints ===")
    
    # Test Google login (should redirect)
    response = requests.get(f"{BASE_URL}/auth/google/login/", allow_redirects=False)
    print(f"Google Login: {response.status_code}")
    if response.status_code == 302:
        print("✅ Google login redirects correctly")
    else:
        print(f"❌ Google login failed: {response.status_code}")
    
    # Test Google token endpoint (should fail without valid token)
    response = requests.post(f"{BASE_URL}/auth/google/token/", json={})
    print(f"Google Token (no data): {response.status_code}")
    if response.status_code == 400:
        print("✅ Google token endpoint validates input")

def test_protected_endpoints(token):
    """Test protected endpoints with authentication"""
    if not token:
        print("\n❌ Skipping protected endpoints test - no token available")
        return
    
    print("\n=== Testing Protected Endpoints ===")
    headers = {"Authorization": f"Token {token}"}
    
    # Test products endpoint
    response = requests.get(f"{BASE_URL}/products/", headers=headers)
    print(f"Products: {response.status_code}")
    if response.status_code == 200:
        print("✅ Products endpoint accessible with token")
    else:
        print(f"❌ Products endpoint failed: {response.text}")
    
    # Test user info
    response = requests.get(f"{BASE_URL}/auth/oidc/userinfo/", headers=headers)
    print(f"OIDC User Info: {response.status_code}")
    if response.status_code == 200:
        print("✅ OIDC user info accessible")
    else:
        print(f"❌ OIDC user info failed: {response.text}")

def main():
    """Run all tests"""
    print("🔐 Testing OrderFlow Authentication System")
    print("=" * 50)
    
    # Test traditional auth
    token = test_traditional_auth()
    
    # Test OIDC endpoints
    test_oidc_endpoints()
    
    # Test Google OAuth2 endpoints
    test_google_oauth_endpoints()
    
    # Test protected endpoints
    test_protected_endpoints(token)
    
    print("\n" + "=" * 50)
    print("🎉 Authentication system test completed!")
    print("\n📝 Next steps:")
    print("1. Configure OIDC provider credentials in .env")
    print("2. Set up Google OAuth2 in Django Admin")
    print("3. Test with real OIDC/Google tokens")

if __name__ == "__main__":
    main()
