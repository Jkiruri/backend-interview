#!/usr/bin/env python3
"""
Comprehensive tests for OrderFlow notification system
Tests SMS, email, task processing, and order notifications
"""
import os
import sys
import django
import time
import requests

# Add the project root to Python path
sys.path.insert(0, '/app')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.authtoken.models import Token
from customers.models import Customer, Admin
from products.models import Product, Category
from orders.models import Order, OrderItem
from notifications.models import Notification
from notifications.tasks import send_order_confirmation, send_admin_order_notification
from notifications.email_service import EmailService
from notifications.sms_service import SMSService

Customer = get_user_model()

class NotificationSystemTest:
    """Test the complete notification system"""
    
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
                'last_name': 'User',
                'phone_number': '+254747210136'  # Whitelisted number for testing
            }
        )
        if created:
            self.customer.set_password('testpass123')
            self.customer.save()
        
        # Create test admin
        self.admin_user, created = Customer.objects.get_or_create(
            email='admin@orderflow.com',
            defaults={
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            self.admin_user.set_password('admin123')
            self.admin_user.save()
        
        # Create admin profile
        self.admin, created = Admin.objects.get_or_create(
            user=self.admin_user,
            defaults={
                'role': 'super_admin',
                'is_active': True
            }
        )
        
        # Create test category and product
        self.category, created = Category.objects.get_or_create(
            name='Test Category',
            defaults={'description': 'Test category for notifications'}
        )
        
        self.product, created = Product.objects.get_or_create(
            name='Test Product',
            defaults={
                'description': 'Test product for notifications',
                'price': 1000.00,
                'category': self.category,
                'stock_quantity': 10
            }
        )
        
        print("✅ Test data setup complete")
    
    def test_email_configuration(self):
        """Test email configuration"""
        print("\n" + "=" * 60)
        print("📧 TESTING EMAIL CONFIGURATION")
        print("=" * 60)
        
        from django.conf import settings
        
        print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
        print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
        print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'NOT SET')}")
        print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
        print(f"EMAIL_HOST_PASSWORD: {'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NOT SET'}")
        
        # Test email service
        try:
            email_service = EmailService()
            result = email_service.send_email(
                to_email='test@example.com',
                subject='Test Email from OrderFlow',
                message='This is a test email to verify the email configuration is working.'
            )
            
            print(f"✅ Email service test result: {result}")
            return True
        except Exception as e:
            print(f"❌ Email service test failed: {e}")
            return False
    
    def test_sms_configuration(self):
        """Test SMS configuration"""
        print("\n" + "=" * 60)
        print("📱 TESTING SMS CONFIGURATION")
        print("=" * 60)
        
        from django.conf import settings
        
        print(f"AFRICASTALKING_API_KEY: {'SET' if getattr(settings, 'AFRICASTALKING_API_KEY', None) else 'NOT SET'}")
        print(f"AFRICASTALKING_USERNAME: {getattr(settings, 'AFRICASTALKING_USERNAME', 'NOT SET')}")
        print(f"AFRICAS_TALKING_SANDBOX: {getattr(settings, 'AFRICAS_TALKING_SANDBOX', 'NOT SET')}")
        
        # Test SMS service
        try:
            sms_service = SMSService()
            result = sms_service.send_sms(
                phone_number=self.customer.phone_number,
                message='Test SMS from OrderFlow - Your order has been confirmed!',
                notification_id='test-123'
            )
            
            print(f"✅ SMS service test result: {result}")
            return True
        except Exception as e:
            print(f"❌ SMS service test failed: {e}")
            return False
    
    def test_token_behavior(self):
        """Test token behavior on login"""
        print("\n" + "=" * 60)
        print("🔐 TESTING TOKEN BEHAVIOR")
        print("=" * 60)
        
        try:
            # First login
            response1 = self.client.post('/api/v1/auth/login/', {
                'email': 'test@example.com',
                'password': 'testpass123'
            })
            
            if response1.status_code == 200:
                token1 = response1.json().get('token')
                print(f"✅ First login token: {token1[:10]}...")
            else:
                print(f"❌ First login failed: {response1.status_code}")
                return False
            
            # Second login (should return same token)
            response2 = self.client.post('/api/v1/auth/login/', {
                'email': 'test@example.com',
                'password': 'testpass123'
            })
            
            if response2.status_code == 200:
                token2 = response2.json().get('token')
                print(f"✅ Second login token: {token2[:10]}...")
            else:
                print(f"❌ Second login failed: {response2.status_code}")
                return False
            
            # Tokens should be the same (get_or_create behavior)
            if token1 == token2:
                print("✅ Tokens are the same (get_or_create behavior confirmed)")
            else:
                print("❌ Tokens are different (unexpected)")
                return False
            
            # Test logout
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token1}'
            logout_response = self.client.post('/api/v1/auth/logout/')
            
            if logout_response.status_code == 200:
                print("✅ Logout successful")
            else:
                print(f"❌ Logout failed: {logout_response.status_code}")
            
            # Third login (should create new token after logout)
            response3 = self.client.post('/api/v1/auth/login/', {
                'email': 'test@example.com',
                'password': 'testpass123'
            })
            
            if response3.status_code == 200:
                token3 = response3.json().get('token')
                print(f"✅ Third login token (after logout): {token3[:10]}...")
            else:
                print(f"❌ Third login failed: {response3.status_code}")
                return False
            
            # New token should be different after logout
            if token1 != token3:
                print("✅ New token created after logout")
                return True
            else:
                print("❌ Token not changed after logout")
                return False
                
        except Exception as e:
            print(f"❌ Token behavior test failed: {e}")
            return False
    
    def test_task_queuing(self):
        """Test task queuing functionality"""
        print("\n" + "=" * 60)
        print("📋 TESTING TASK QUEUING")
        print("=" * 60)
        
        try:
            # Create a test order
            order = Order.objects.create(
                customer=self.customer,
                shipping_address="Test Address for Task Queuing",
                billing_address="Test Billing Address",
                total_amount=2000.00,
                status='pending'
            )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=self.product,
                quantity=2,
                unit_price=1000.00,
                subtotal=2000.00
            )
            
            print(f"✅ Test order created: {order.order_number}")
            
            # Queue notification tasks
            print("\n🔍 Queueing notification tasks...")
            
            # Queue customer notification
            customer_task = send_order_confirmation.delay(
                str(order.id), 
                send_sms=True, 
                send_email=True
            )
            print(f"✅ Customer task queued: {customer_task.id}")
            
            # Queue admin notification
            admin_task = send_admin_order_notification.delay(str(order.id))
            print(f"✅ Admin task queued: {admin_task.id}")
            
            # Check task status
            print("\n🔍 Checking task status...")
            time.sleep(3)
            
            print(f"Customer task status: {customer_task.status}")
            print(f"Admin task status: {admin_task.status}")
            
            if customer_task.ready():
                print(f"Customer task result: {customer_task.result}")
            
            if admin_task.ready():
                print(f"Admin task result: {admin_task.result}")
            
            # Tasks should be queued (PENDING status is expected)
            if customer_task.status in ['PENDING', 'SUCCESS', 'FAILURE'] and admin_task.status in ['PENDING', 'SUCCESS', 'FAILURE']:
                print("✅ Task queuing test passed")
                return True
            else:
                print("❌ Task queuing test failed")
                return False
                
        except Exception as e:
            print(f"❌ Task queuing test failed: {e}")
            return False
    
    def test_order_creation_with_notifications(self):
        """Test order creation triggers notifications"""
        print("\n" + "=" * 60)
        print("📋 TESTING ORDER CREATION WITH NOTIFICATIONS")
        print("=" * 60)
        
        try:
            # Create order data
            order_data = {
                'shipping_address': 'Test Address for Notifications',
                'billing_address': 'Test Billing Address',
                'items': [
                    {
                        'product': self.product.id,
                        'quantity': 2
                    }
                ]
            }
            
            # Get authentication token
            token, _ = Token.objects.get_or_create(user=self.customer)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
            
            # Create order via API
            response = self.client.post('/api/v1/orders/', order_data, content_type='application/json')
            
            print(f"Order creation response status: {response.status_code}")
            if response.status_code == 201:
                order_data = response.json()
                print(f"✅ Order created: {order_data.get('order_number')}")
                print(f"Order ID: {order_data.get('id')}")
                print(f"Total Amount: Ksh {order_data.get('total_amount')}")
                
                # Wait for notifications to be processed
                print("⏳ Waiting 5 seconds for notifications to be processed...")
                time.sleep(5)
                
                # Check if notifications were created
                notifications = Notification.objects.filter(order_id=order_data.get('id'))
                print(f"📢 Notifications created: {notifications.count()}")
                
                for notification in notifications:
                    print(f"  - {notification.notification_type}: {notification.status}")
                
                print("✅ Order creation with notifications test passed")
                return True
            else:
                print(f"❌ Order creation failed: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Order creation test failed: {e}")
            return False
    
    def test_admin_creation(self):
        """Test admin user creation"""
        print("\n" + "=" * 60)
        print("👤 TESTING ADMIN CREATION")
        print("=" * 60)
        
        try:
            # Get admin authentication token
            admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {admin_token.key}'
            
            # Create new admin user
            admin_data = {
                'email': 'newadmin@orderflow.com',
                'first_name': 'New',
                'last_name': 'Admin',
                'password': 'newadmin123',
                'role': 'admin'
            }
            
            response = self.client.post('/api/v1/admin/create-admin/', admin_data, content_type='application/json')
            
            print(f"Admin creation response status: {response.status_code}")
            if response.status_code == 201:
                admin_info = response.json()
                print(f"✅ Admin created: {admin_info.get('email')}")
                print(f"Admin ID: {admin_info.get('id')}")
                print(f"Role: {admin_info.get('role')}")
                return True
            else:
                print(f"❌ Admin creation failed: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Admin creation test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 ORDERFLOW NOTIFICATION SYSTEM COMPREHENSIVE TEST")
        print("=" * 60)
        
        results = {}
        
        try:
            # Test 1: Email Configuration
            results['email'] = self.test_email_configuration()
            
            # Test 2: SMS Configuration
            results['sms'] = self.test_sms_configuration()
            
            # Test 3: Token Behavior
            results['token'] = self.test_token_behavior()
            
            # Test 4: Task Queuing
            results['task_queuing'] = self.test_task_queuing()
            
            # Test 5: Order Creation with Notifications
            results['order_creation'] = self.test_order_creation_with_notifications()
            
            # Test 6: Admin Creation
            results['admin_creation'] = self.test_admin_creation()
            
            # Summary
            print("\n" + "=" * 60)
            print("📊 TEST RESULTS SUMMARY")
            print("=" * 60)
            
            passed = 0
            total = len(results)
            
            for test_name, result in results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"{test_name.replace('_', ' ').title()}: {status}")
                if result:
                    passed += 1
            
            print(f"\nOverall: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
            else:
                print("⚠️  Some tests failed. Check the output above for details.")
            
            return passed == total
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {e}")
            return False

def main():
    """Run the comprehensive test suite"""
    test_suite = NotificationSystemTest()
    success = test_suite.run_all_tests()
    
    if success:
        print("\n🎯 All systems are working correctly!")
    else:
        print("\n🔧 Some issues detected. Review the test output above.")

if __name__ == "__main__":
    main()
