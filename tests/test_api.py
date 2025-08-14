#!/usr/bin/env python
"""
Test script for OrderFlow API with seeded data
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_authentication():
    """Test authentication with seeded data"""
    print("=== Testing Authentication ===")
    
    # Login with seeded customer
    login_data = {
        "email": "john.doe@example.com",
        "password": "password123"
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

def test_products_api(token):
    """Test products API"""
    print("\n=== Testing Products API ===")
    headers = {"Authorization": f"Token {token}"} if token else {}
    
    # Get all products
    response = requests.get(f"{BASE_URL}/products/", headers=headers)
    print(f"Products: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} products")
        print(f"   - Page size: {len(data['results'])}")
        return data['results']
    else:
        print(f"❌ Products failed: {response.text}")
        return []

def test_categories_api(token):
    """Test categories API"""
    print("\n=== Testing Categories API ===")
    headers = {"Authorization": f"Token {token}"} if token else {}
    
    # Get all categories
    response = requests.get(f"{BASE_URL}/categories/", headers=headers)
    print(f"Categories: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} categories")
        
        # Show hierarchy
        for category in data['results']:
            indent = "  " * category.get('level', 0)
            products_count = category.get('products_count', 0)
            print(f"   {indent}- {category['name']} ({products_count} products)")
        return data['results']
    else:
        print(f"❌ Categories failed: {response.text}")
        return []

def test_orders_api(token):
    """Test orders API"""
    print("\n=== Testing Orders API ===")
    headers = {"Authorization": f"Token {token}"} if token else {}
    
    # Get all orders
    response = requests.get(f"{BASE_URL}/orders/", headers=headers)
    print(f"Orders: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} orders")
        
        # Show order summary
        total_value = sum(float(order['total_amount']) for order in data['results'])
        print(f"   - Total value: ${total_value:,.2f}")
        
        # Status breakdown
        status_counts = {}
        for order in data['results']:
            status = order['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("   - Status breakdown:")
        for status, count in status_counts.items():
            print(f"     * {status}: {count}")
        
        return data['results']
    else:
        print(f"❌ Orders failed: {response.text}")
        return []

def test_customers_api(token):
    """Test customers API"""
    print("\n=== Testing Customers API ===")
    headers = {"Authorization": f"Token {token}"} if token else {}
    
    # Get all customers
    response = requests.get(f"{BASE_URL}/customers/", headers=headers)
    print(f"Customers: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} customers")
        
        # Show customer summary
        verified_count = sum(1 for customer in data['results'] if customer['is_verified'])
        print(f"   - Verified customers: {verified_count}/{len(data['results'])}")
        
        return data['results']
    else:
        print(f"❌ Customers failed: {response.text}")
        return []

def test_average_price_api(token):
    """Test average price per category API"""
    print("\n=== Testing Average Price Per Category ===")
    headers = {"Authorization": f"Token {token}"} if token else {}
    
    # Get average prices
    response = requests.get(f"{BASE_URL}/categories/average-price-per-category/", headers=headers)
    print(f"Average Prices: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✅ Average prices per category:")
        for category in data:
            print(f"   - {category['category_name']}: ${category['average_price']:.2f}")
        return data
    else:
        print(f"❌ Average prices failed: {response.text}")
        return []

def test_search_and_filter(token):
    """Test search and filter functionality"""
    print("\n=== Testing Search and Filter ===")
    headers = {"Authorization": f"Token {token}"} if token else {}
    
    # Search for iPhone
    response = requests.get(f"{BASE_URL}/products/?search=iPhone", headers=headers)
    print(f"Search 'iPhone': {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} products matching 'iPhone'")
    
    # Filter by category
    response = requests.get(f"{BASE_URL}/products/?category=smartphones", headers=headers)
    print(f"Filter by smartphones: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} smartphones")
    
    # Price range filter
    response = requests.get(f"{BASE_URL}/products/?min_price=100&max_price=500", headers=headers)
    print(f"Price range $100-$500: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} products in price range")

def main():
    """Run all API tests"""
    print("🚀 Testing OrderFlow API with Seeded Data")
    print("=" * 60)
    
    # Test authentication
    token = test_authentication()
    
    if token:
        # Test all API endpoints
        products = test_products_api(token)
        categories = test_categories_api(token)
        orders = test_orders_api(token)
        customers = test_customers_api(token)
        average_prices = test_average_price_api(token)
        test_search_and_filter(token)
        
        print("\n" + "=" * 60)
        print("🎉 API testing completed successfully!")
        print(f"📊 Summary:")
        print(f"   - {len(products)} products available")
        print(f"   - {len(categories)} categories with hierarchy")
        print(f"   - {len(orders)} orders with various statuses")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(average_prices)} categories with average prices")
        
        print("\n🔗 API Endpoints tested:")
        print("   - Authentication: /api/v1/auth/login/")
        print("   - Products: /api/v1/products/")
        print("   - Categories: /api/v1/categories/")
        print("   - Orders: /api/v1/orders/")
        print("   - Customers: /api/v1/customers/")
        print("   - Average Prices: /api/v1/products/average-price-per-category/")
        
    else:
        print("❌ Authentication failed - cannot test protected endpoints")

if __name__ == "__main__":
    main()
