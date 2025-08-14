#!/usr/bin/env python3
"""
Test script to verify registration endpoint works without CSRF issues
"""
import requests
import json

def test_registration():
    """Test the registration endpoint"""
    url = "http://localhost:8000/api/v1/auth/register/"
    
    # Test data
    data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            response_data = response.json()
            print(f"Customer ID: {response_data['customer']['id']}")
            print(f"Token: {response_data['token'][:20]}...")
        elif response.status_code == 400:
            print("⚠️  Registration failed - validation error")
            errors = response.json()
            if 'email' in errors:
                print(f"Email error: {errors['email']}")
        elif response.status_code == 403:
            print("❌ CSRF error still present")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration()
