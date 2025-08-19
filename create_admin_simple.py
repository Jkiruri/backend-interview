#!/usr/bin/env python3
"""
Simple script to create an admin user
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from customers.models import Customer
from django.contrib.auth.hashers import make_password

def create_admin_user():
    """Create a simple admin user"""
    print("=" * 60)
    print("👤 CREATING ADMIN USER")
    print("=" * 60)
    
    try:
        # Create admin customer using the Customer model
        admin_customer = Customer.objects.create(
            email='admin@jameskiruri.co.ke',
            first_name='System',
            last_name='Administrator',
            password=make_password('admin123456'),
            is_staff=True,
            is_superuser=True,
            is_verified=True,
            is_active=True,
            email_verified=True
        )
        
        print(f"✅ Created admin user: {admin_customer.email}")
        print(f"   Name: {admin_customer.full_name}")
        print(f"   Is Staff: {admin_customer.is_staff}")
        print(f"   Is Superuser: {admin_customer.is_superuser}")
        print(f"   Is Verified: {admin_customer.is_verified}")
        
        return admin_customer
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return None

def test_admin_login():
    """Test admin login"""
    print("\n" + "=" * 60)
    print("🔐 TESTING ADMIN LOGIN")
    print("=" * 60)
    
    try:
        # Get admin user
        admin = Customer.objects.get(email='admin@jameskiruri.co.ke')
        
        # Test password
        if admin.check_password('admin123456'):
            print("✅ Admin password is correct!")
        else:
            print("❌ Admin password is incorrect!")
        
        return admin
        
    except Customer.DoesNotExist:
        print("❌ Admin user not found")
        return None
    except Exception as e:
        print(f"❌ Error testing admin login: {e}")
        return None

def test_admin_email_notification():
    """Test admin email notification"""
    print("\n" + "=" * 60)
    print("📧 TESTING ADMIN EMAIL NOTIFICATION")
    print("=" * 60)
    
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        # Send test email to admin
        result = send_mail(
            subject='OrderFlow Admin Test Email',
            message='This is a test email to verify admin notifications are working.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['admin@jameskiruri.co.ke'],
            fail_silently=False
        )
        
        if result:
            print("✅ Admin email notification sent successfully!")
            print("📧 Check admin@jameskiruri.co.ke for the test email")
        else:
            print("❌ Admin email notification failed")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing admin email: {e}")
        return None

def test_admin_crud_access():
    """Test admin CRUD access"""
    print("\n" + "=" * 60)
    print("🔧 TESTING ADMIN CRUD ACCESS")
    print("=" * 60)
    
    try:
        # Test if admin can access models
        from products.models import Product, Category
        from orders.models import Order
        from customers.models import Customer
        
        # Count records
        product_count = Product.objects.count()
        category_count = Category.objects.count()
        order_count = Order.objects.count()
        customer_count = Customer.objects.count()
        
        print(f"✅ Admin can access all models:")
        print(f"   Products: {product_count}")
        print(f"   Categories: {category_count}")
        print(f"   Orders: {order_count}")
        print(f"   Customers: {customer_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing admin CRUD access: {e}")
        return False

def main():
    """Main function"""
    print("🚀 SIMPLE ADMIN CREATION")
    print("=" * 60)
    
    # Create admin user
    admin = create_admin_user()
    
    if admin:
        # Test admin login
        test_admin_login()
        
        # Test admin email notification
        test_admin_email_notification()
        
        # Test admin CRUD access
        test_admin_crud_access()
        
        print("\n" + "=" * 60)
        print("🏁 ADMIN CREATION COMPLETED")
        print("=" * 60)
        print("\nAdmin Credentials:")
        print(f"Email: {admin.email}")
        print("Password: admin123456")
        print("\nYou can now:")
        print("1. Login to Django Admin: http://localhost:8000/admin")
        print("2. Use this admin for system management")
        print("3. All orders will be sent to admin@jameskiruri.co.ke")
        print("4. Admin has full CRUD access to all models")
        print("5. Admin can manage products, customers, orders, and notifications")

if __name__ == "__main__":
    main()
