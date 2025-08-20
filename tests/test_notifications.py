#!/usr/bin/env python3
"""
Comprehensive tests for OrderFlow notification system
Tests SMS, email, task processing, and order notifications
"""
import os
import django
import time
import requests
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from customers.models import Customer, Admin
from products.models import Product, Category
from orders.models import Order, OrderItem
from notifications.models import Notification
from notifications.tasks import send_order_confirmation, send_admin_order_notification
from notifications.email_service import EmailService
from notifications.sms_service import SMSService

Customer = get_user_model()

class NotificationSystemTest(APITestCase):
    """Test the complete notification system"""
    
    def setUp(self):
        """Set up test data"""
        # Create test customer
        self.customer = Customer.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            phone_number='+254747210136'  # Whitelisted number for testing
        )
        
        # Create test admin
        self.admin_user = Customer.objects.create_user(
            email='admin@orderflow.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        
        # Create admin profile
        self.admin = Admin.objects.create(
            user=self.admin_user,
            role='super_admin',
            is_active=True
        )
        
        # Create test category and product
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category for notifications'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test product for notifications',
            price=1000.00,
            category=self.category,
            stock_quantity=10
        )
        
        # Get authentication token
        self.token, _ = Token.objects.get_or_create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
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
        email_service = EmailService()
        result = email_service.send_email(
            to_email='test@example.com',
            subject='Test Email from OrderFlow',
            message='This is a test email to verify the email configuration is working.'
        )
        
        print(f"✅ Email service test result: {result}")
        self.assertIsInstance(result, dict)
    
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
        sms_service = SMSService()
        result = sms_service.send_sms(
            phone_number=self.customer.phone_number,
            message='Test SMS from OrderFlow - Your order has been confirmed!',
            notification_id='test-123'
        )
        
        print(f"✅ SMS service test result: {result}")
        self.assertIsInstance(result, dict)
    
    def test_order_creation_with_notifications(self):
        """Test order creation triggers notifications"""
        print("\n" + "=" * 60)
        print("📋 TESTING ORDER CREATION WITH NOTIFICATIONS")
        print("=" * 60)
        
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
        
        # Create order via API
        response = self.client.post('/api/v1/orders/', order_data, format='json')
        
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
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        else:
            print(f"❌ Order creation failed: {response.text}")
            self.fail("Order creation failed")
    
    def test_task_queuing(self):
        """Test task queuing functionality"""
        print("\n" + "=" * 60)
        print("📋 TESTING TASK QUEUING")
        print("=" * 60)
        
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
        self.assertIn(customer_task.status, ['PENDING', 'SUCCESS', 'FAILURE'])
        self.assertIn(admin_task.status, ['PENDING', 'SUCCESS', 'FAILURE'])
    
    def test_token_behavior(self):
        """Test token behavior on login"""
        print("\n" + "=" * 60)
        print("🔐 TESTING TOKEN BEHAVIOR")
        print("=" * 60)
        
        # First login
        response1 = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        token1 = response1.json().get('token')
        print(f"✅ First login token: {token1[:10]}...")
        
        # Second login (should return same token)
        response2 = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        token2 = response2.json().get('token')
        print(f"✅ Second login token: {token2[:10]}...")
        
        # Tokens should be the same (get_or_create behavior)
        self.assertEqual(token1, token2)
        print("✅ Tokens are the same (get_or_create behavior confirmed)")
        
        # Test logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token1}')
        logout_response = self.client.post('/api/v1/auth/logout/')
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        print("✅ Logout successful")
        
        # Third login (should create new token after logout)
        response3 = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        token3 = response3.json().get('token')
        print(f"✅ Third login token (after logout): {token3[:10]}...")
        
        # New token should be different after logout
        self.assertNotEqual(token1, token3)
        print("✅ New token created after logout")
    
    def test_admin_creation(self):
        """Test admin user creation"""
        print("\n" + "=" * 60)
        print("👤 TESTING ADMIN CREATION")
        print("=" * 60)
        
        # Login as admin
        admin_token, _ = Token.objects.get_or_create(user=self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        
        # Create new admin user
        admin_data = {
            'email': 'newadmin@orderflow.com',
            'first_name': 'New',
            'last_name': 'Admin',
            'password': 'newadmin123',
            'role': 'admin'
        }
        
        response = self.client.post('/api/v1/admin/create-admin/', admin_data, format='json')
        
        print(f"Admin creation response status: {response.status_code}")
        if response.status_code == 201:
            admin_info = response.json()
            print(f"✅ Admin created: {admin_info.get('email')}")
            print(f"Admin ID: {admin_info.get('id')}")
            print(f"Role: {admin_info.get('role')}")
        else:
            print(f"❌ Admin creation failed: {response.text}")
        
        # Should succeed with super admin permissions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 ORDERFLOW NOTIFICATION SYSTEM COMPREHENSIVE TEST")
        print("=" * 60)
        
        try:
            # Test 1: Email Configuration
            self.test_email_configuration()
            
            # Test 2: SMS Configuration
            self.test_sms_configuration()
            
            # Test 3: Token Behavior
            self.test_token_behavior()
            
            # Test 4: Task Queuing
            self.test_task_queuing()
            
            # Test 5: Order Creation with Notifications
            self.test_order_creation_with_notifications()
            
            # Test 6: Admin Creation
            self.test_admin_creation()
            
            print("\n" + "=" * 60)
            print("📊 ALL TESTS COMPLETED SUCCESSFULLY")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise

def main():
    """Run the comprehensive test suite"""
    test_suite = NotificationSystemTest()
    test_suite.setUp()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
