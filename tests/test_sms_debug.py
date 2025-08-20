#!/usr/bin/env python3
"""
SMS debugging test for OrderFlow
Tests SMS notifications for orders
"""
import os
import sys
import django
import time

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
from notifications.sms_service import SMSService
from notifications.email_service import EmailService

Customer = get_user_model()

class SMSDebugTest:
    """Test SMS notification functionality"""
    
    def __init__(self):
        """Initialize test environment"""
        self.client = Client()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Set up test data"""
        print("🔧 Setting up test data...")
        
        # Create test customer with phone number
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
            defaults={'description': 'Test category for SMS'}
        )
        
        self.product, created = Product.objects.get_or_create(
            name='Test Product',
            defaults={
                'description': 'Test product for SMS',
                'price': 1000.00,
                'category': self.category,
                'stock_quantity': 10
            }
        )
        
        print("✅ Test data setup complete")
    
    def test_sms_service_direct(self):
        """Test SMS service directly"""
        print("\n" + "=" * 60)
        print("📱 SMS SERVICE DIRECT TEST")
        print("=" * 60)
        
        try:
            sms_service = SMSService()
            result = sms_service.send_sms(
                phone_number=self.customer.phone_number,
                message='Test SMS from OrderFlow - Direct service test!',
                notification_id='test-sms-123'
            )
            
            print(f"✅ SMS service test result: {result}")
            return result.get('success', False)
            
        except Exception as e:
            print(f"❌ SMS service test failed: {e}")
            return False
    
    def test_order_confirmation_task(self):
        """Test order confirmation task with SMS"""
        print("\n" + "=" * 60)
        print("📋 ORDER CONFIRMATION TASK WITH SMS")
        print("=" * 60)
        
        try:
            # Create a test order
            order = Order.objects.create(
                customer=self.customer,
                shipping_address="Test Address for SMS",
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
            print(f"Customer phone: {order.customer.phone_number}")
            
            # Test order confirmation task with SMS enabled
            task = send_order_confirmation.delay(
                str(order.id), 
                send_sms=True, 
                send_email=True
            )
            
            print(f"✅ Order confirmation task queued: {task.id}")
            
            # Wait for task to be processed
            print("⏳ Waiting 10 seconds for task processing...")
            time.sleep(10)
            
            print(f"Task status: {task.status}")
            
            if task.ready():
                result = task.result
                print(f"Task result: {result}")
                
                # Check if SMS was sent
                if result and isinstance(result, dict):
                    sms_result = result.get('sms')
                    if sms_result:
                        print(f"✅ SMS result: {sms_result}")
                        return sms_result.get('success', False)
                    else:
                        print("❌ No SMS result in task response")
                        return False
                else:
                    print("❌ Invalid task result format")
                    return False
            else:
                print("❌ Task not completed within timeout")
                return False
                
        except Exception as e:
            print(f"❌ Order confirmation task test failed: {e}")
            return False
    
    def test_order_creation_with_sms(self):
        """Test order creation via API with SMS notifications"""
        print("\n" + "=" * 60)
        print("📋 ORDER CREATION VIA API WITH SMS")
        print("=" * 60)
        
        try:
            # Get authentication token
            token, _ = Token.objects.get_or_create(user=self.customer)
            self.client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
            
            # Create order data
            order_data = {
                'shipping_address': 'Test Address for SMS API',
                'billing_address': 'Test Billing Address',
                'phone_number': '+254747210136',  # Ensure phone number is included
                'items': [
                    {
                        'product_id': self.product.id,
                        'quantity': 2
                    }
                ]
            }
            
            # Create order via API
            response = self.client.post('/api/v1/orders/', order_data, content_type='application/json')
            
            print(f"Order creation response status: {response.status_code}")
            if response.status_code == 201:
                order_data = response.json()
                print(f"✅ Order created: {order_data.get('order_number')}")
                print(f"Order ID: {order_data.get('id')}")
                
                # Wait for notifications to be processed
                print("⏳ Waiting 10 seconds for notifications to be processed...")
                time.sleep(10)
                
                # Check if SMS notifications were created
                notifications = Notification.objects.filter(
                    order_id=order_data.get('id'),
                    notification_type='sms'
                )
                print(f"📱 SMS notifications created: {notifications.count()}")
                
                for notification in notifications:
                    print(f"  - SMS notification: {notification.status}")
                    print(f"    Message: {notification.message[:100]}...")
                
                return notifications.count() > 0
            else:
                print(f"❌ Order creation failed: {response.content.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Order creation test failed: {e}")
            return False
    
    def check_sms_notifications(self):
        """Check all SMS notifications in the system"""
        print("\n" + "=" * 60)
        print("📱 SMS NOTIFICATIONS CHECK")
        print("=" * 60)
        
        try:
            # Get all SMS notifications
            sms_notifications = Notification.objects.filter(notification_type='sms').order_by('-created_at')[:10]
            
            print(f"Total SMS notifications found: {sms_notifications.count()}")
            
            for notification in sms_notifications:
                print(f"\n📱 SMS Notification:")
                print(f"  - ID: {notification.id}")
                print(f"  - Status: {notification.status}")
                print(f"  - Recipient: {notification.recipient.phone_number}")
                print(f"  - Order: {notification.order.order_number if notification.order else 'N/A'}")
                print(f"  - Created: {notification.created_at}")
                print(f"  - Message: {notification.message[:100]}...")
            
            return sms_notifications.count() > 0
            
        except Exception as e:
            print(f"❌ SMS notifications check failed: {e}")
            return False
    
    def run_sms_tests(self):
        """Run all SMS tests"""
        print("🚀 ORDERFLOW SMS DEBUGGING TEST")
        print("=" * 60)
        
        results = {}
        
        # Test 1: SMS Service Direct
        results['sms_service'] = self.test_sms_service_direct()
        
        # Test 2: Order Confirmation Task
        results['order_confirmation'] = self.test_order_confirmation_task()
        
        # Test 3: Order Creation via API
        results['order_creation'] = self.test_order_creation_with_sms()
        
        # Test 4: Check SMS Notifications
        results['sms_notifications'] = self.check_sms_notifications()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SMS DEBUG RESULTS")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} SMS tests passed")
        
        if passed == total:
            print("🎉 All SMS tests passed! SMS system is working.")
        else:
            print("🔧 Some SMS issues detected. Check the output above for details.")
        
        return passed == total

def main():
    """Run the SMS debugging test suite"""
    test_suite = SMSDebugTest()
    success = test_suite.run_sms_tests()
    
    if success:
        print("\n🎯 SMS notification system is working correctly!")
    else:
        print("\n🔧 Some SMS issues detected. Review the test output above.")

if __name__ == "__main__":
    main()
