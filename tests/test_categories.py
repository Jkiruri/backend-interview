#!/usr/bin/env python3
"""
Category endpoint test for OrderFlow
Tests category endpoints and creates test data
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.authtoken.models import Token
from products.models import Category, Product
from customers.models import Admin

Customer = get_user_model()

class CategoryTest:
    """Test category endpoints and functionality"""
    
    def __init__(self):
        """Initialize test environment"""
        self.client = Client()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Set up test data"""
        print("🔧 Setting up test data...")
        
        # Create test customer
        self.customer, created = Customer.objects.get_or_create(
            email='test@example.com',
            defaults={
                'password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            self.customer.set_password('testpass123')
            self.customer.save()
        
        # Create test categories
        self.accessories_category, created = Category.objects.get_or_create(
            name='Accessories',
            defaults={
                'description': 'Electronic accessories and gadgets',
                'slug': 'accessories'
            }
        )
        
        self.electronics_category, created = Category.objects.get_or_create(
            name='Electronics',
            defaults={
                'description': 'Electronic devices and equipment',
                'slug': 'electronics'
            }
        )
        
        self.clothing_category, created = Category.objects.get_or_create(
            name='Clothing',
            defaults={
                'description': 'Fashion and apparel',
                'slug': 'clothing'
            }
        )
        
        # Create test products
        self.product1, created = Product.objects.get_or_create(
            name='Test Product 1',
            defaults={
                'description': 'Test product for accessories',
                'price': 1000.00,
                'category': self.accessories_category,
                'stock_quantity': 10,
                'status': 'active'
            }
        )
        
        self.product2, created = Product.objects.get_or_create(
            name='Test Product 2',
            defaults={
                'description': 'Test product for electronics',
                'price': 2000.00,
                'category': self.electronics_category,
                'stock_quantity': 5,
                'status': 'active'
            }
        )
        
        self.product3, created = Product.objects.get_or_create(
            name='Test Product 3',
            defaults={
                'description': 'Test product for clothing',
                'price': 500.00,
                'category': self.clothing_category,
                'stock_quantity': 20,
                'status': 'active'
            }
        )
        
        print("✅ Test data setup complete")
        print(f"Categories created: {Category.objects.count()}")
        print(f"Products created: {Product.objects.count()}")
    
    def test_category_list(self):
        """Test category list endpoint"""
        print("\n" + "=" * 60)
        print("📋 CATEGORY LIST TEST")
        print("=" * 60)
        
        try:
            # Get authentication token
            token, _ = Token.objects.get_or_create(user=self.customer)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
            
            # Test category list
            response = self.client.get('/api/v1/categories/')
            
            print(f"Category list response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Categories found: {len(data.get('results', data))}")
                for category in data.get('results', data):
                    print(f"  - {category.get('name')} (slug: {category.get('slug')})")
                return True
            else:
                print(f"❌ Category list failed: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Category list test failed: {e}")
            return False
    
    def test_category_average_price(self):
        """Test category average price endpoint"""
        print("\n" + "=" * 60)
        print("💰 CATEGORY AVERAGE PRICE TEST")
        print("=" * 60)
        
        try:
            # Get authentication token
            token, _ = Token.objects.get_or_create(user=self.customer)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
            
            # Test with accessories category
            response = self.client.get('/api/v1/categories/average_price/?slug=accessories')
            
            print(f"Average price response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Average price data:")
                print(f"  - Category: {data.get('category_name')}")
                print(f"  - Average Price: {data.get('average_price')}")
                print(f"  - Product Count: {data.get('product_count')}")
                print(f"  - Min Price: {data.get('min_price')}")
                print(f"  - Max Price: {data.get('max_price')}")
                return True
            else:
                print(f"❌ Average price failed: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Average price test failed: {e}")
            return False
    
    def test_category_average_price_per_category(self):
        """Test category average price per category endpoint"""
        print("\n" + "=" * 60)
        print("💰 CATEGORY AVERAGE PRICE PER CATEGORY TEST")
        print("=" * 60)
        
        try:
            # Get authentication token
            token, _ = Token.objects.get_or_create(user=self.customer)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
            
            # Test average price per category
            response = self.client.get('/api/v1/categories/average_price_per_category/')
            
            print(f"Average price per category response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Average price per category data:")
                for category_data in data:
                    print(f"  - {category_data.get('category_name')}: ${category_data.get('average_price')} ({category_data.get('product_count')} products)")
                return True
            else:
                print(f"❌ Average price per category failed: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Average price per category test failed: {e}")
            return False
    
    def test_category_tree(self):
        """Test category tree endpoint"""
        print("\n" + "=" * 60)
        print("🌳 CATEGORY TREE TEST")
        print("=" * 60)
        
        try:
            # Get authentication token
            token, _ = Token.objects.get_or_create(user=self.customer)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
            
            # Test category tree
            response = self.client.get('/api/v1/categories/tree/')
            
            print(f"Category tree response status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Category tree data:")
                for category in data:
                    print(f"  - {category.get('name')} (children: {len(category.get('children', []))})")
                return True
            else:
                print(f"❌ Category tree failed: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Category tree test failed: {e}")
            return False
    
    def check_available_urls(self):
        """Check what category URLs are available"""
        print("\n" + "=" * 60)
        print("🔗 AVAILABLE CATEGORY URLS")
        print("=" * 60)
        
        try:
            # Get authentication token
            token, _ = Token.objects.get_or_create(user=self.customer)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
            
            # Test various URL patterns
            urls_to_test = [
                '/api/v1/categories/',
                '/api/v1/categories/average_price/',
                '/api/v1/categories/average_price_per_category/',
                '/api/v1/categories/tree/',
                '/api/v1/categories/1/',
                '/api/v1/categories/1/average_price/',
            ]
            
            for url in urls_to_test:
                response = self.client.get(url)
                print(f"{url}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ URL check failed: {e}")
    
    def run_category_tests(self):
        """Run all category tests"""
        print("🚀 ORDERFLOW CATEGORY ENDPOINT TEST")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Category List
        results['category_list'] = self.test_category_list()
        
        # Test 2: Category Average Price
        results['category_average_price'] = self.test_category_average_price()
        
        # Test 3: Category Average Price Per Category
        results['category_average_price_per_category'] = self.test_category_average_price_per_category()
        
        # Test 4: Category Tree
        results['category_tree'] = self.test_category_tree()
        
        # Check available URLs
        self.check_available_urls()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CATEGORY TEST RESULTS")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} category tests passed")
        
        if passed == total:
            print("🎉 All category tests passed! Category endpoints are working.")
        else:
            print("🔧 Some category issues detected. Check the output above for details.")
        
        return passed == total

def main():
    """Run the category test suite"""
    test_suite = CategoryTest()
    success = test_suite.run_category_tests()
    
    if success:
        print("\n🎯 Category endpoints are working correctly!")
    else:
        print("\n🔧 Some category issues detected. Review the test output above.")

if __name__ == "__main__":
    main()
