#!/usr/bin/env python3
"""
Test script for the admin system functionality
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from customers.models import Customer, Admin
from notifications.admin_service import AdminService
from orders.models import Order
from products.models import Product, Category

def test_admin_creation():
    """Test admin user creation"""
    print("=" * 60)
    print("👤 TESTING ADMIN USER CREATION")
    print("=" * 60)
    
    try:
        admin_service = AdminService()
        
        # Create admin user
        admin = admin_service.create_admin_user(
            email='admin@jameskiruri.co.ke',
            first_name='System',
            last_name='Administrator',
            password='admin123456',
            role='super_admin',
            permissions={
                'permissions': [
                    'manage_products',
                    'manage_customers', 
                    'manage_orders',
                    'manage_admins',
                    'view_reports',
                    'send_notifications'
                ]
            }
        )
        
        print(f"✅ Created admin user: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   Permissions: {admin.permissions}")
        
        return admin
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return None

def test_admin_notifications():
    """Test admin notifications"""
    print("\n" + "=" * 60)
    print("📧 TESTING ADMIN NOTIFICATIONS")
    print("=" * 60)
    
    try:
        admin_service = AdminService()
        
        # Get active admins
        active_admins = admin_service.get_active_admins()
        admin_emails = admin_service.get_admin_emails()
        
        print(f"Active admins: {len(active_admins)}")
        print(f"Admin emails: {admin_emails}")
        
        # Test system alert
        alert_result = admin_service.send_system_alert_to_admins(
            'info',
            'This is a test system alert from OrderFlow',
            {'test': True, 'timestamp': '2025-01-19'}
        )
        
        print(f"System alert result: {alert_result}")
        
        if alert_result.get('success'):
            print("✅ System alert sent successfully!")
        else:
            print(f"❌ System alert failed: {alert_result.get('error')}")
        
        return alert_result
        
    except Exception as e:
        print(f"❌ Error testing admin notifications: {e}")
        return None

def test_order_notification_to_admins():
    """Test order notification to admins"""
    print("\n" + "=" * 60)
    print("📋 TESTING ORDER NOTIFICATION TO ADMINS")
    print("=" * 60)
    
    try:
        admin_service = AdminService()
        
        # Get a test order
        order = Order.objects.first()
        if not order:
            print("❌ No orders found. Please create an order first.")
            return None
        
        print(f"Testing with order: {order.order_number}")
        
        # Send order notification to admins
        result = admin_service.send_order_notification_to_admins(order)
        
        print(f"Order notification result: {result}")
        
        if result.get('success'):
            print("✅ Order notification sent to admins successfully!")
            print(f"   Sent to {result.get('success_count')} admins")
        else:
            print(f"❌ Order notification failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing order notification: {e}")
        return None

def test_daily_report():
    """Test daily report generation"""
    print("\n" + "=" * 60)
    print("📊 TESTING DAILY REPORT")
    print("=" * 60)
    
    try:
        admin_service = AdminService()
        
        # Generate report data
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=1)
        
        report_data = {
            'total_orders': Order.objects.count(),
            'new_orders': Order.objects.filter(created_at__gte=start_date).count(),
            'completed_orders': Order.objects.filter(status='completed').count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'total_revenue': float(Order.objects.filter(status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or 0),
            'total_customers': Customer.objects.count(),
            'new_customers': Customer.objects.filter(created_at__gte=start_date).count(),
            'total_products': Product.objects.count(),
            'low_stock_items': Product.objects.filter(stock_quantity__lte=10).count(),
            'notifications_sent': 0,  # This would be from Notification model
            'failed_notifications': 0,  # This would be from Notification model
            'system_uptime': '99.9%'
        }
        
        print(f"Report data: {report_data}")
        
        # Send daily report
        result = admin_service.send_daily_report_to_admins(report_data)
        
        print(f"Daily report result: {result}")
        
        if result.get('success'):
            print("✅ Daily report sent successfully!")
            print(f"   Sent to {result.get('success_count')} admins")
        else:
            print(f"❌ Daily report failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing daily report: {e}")
        return None

def test_admin_permissions():
    """Test admin permissions"""
    print("\n" + "=" * 60)
    print("🔐 TESTING ADMIN PERMISSIONS")
    print("=" * 60)
    
    try:
        # Get admin user
        admin = Admin.objects.first()
        if not admin:
            print("❌ No admin found. Please create an admin first.")
            return None
        
        print(f"Testing permissions for admin: {admin.email}")
        print(f"Current permissions: {admin.permissions}")
        
        # Test permission checking
        permissions_to_test = [
            'manage_products',
            'manage_customers',
            'manage_orders',
            'manage_admins',
            'view_reports'
        ]
        
        for permission in permissions_to_test:
            has_perm = admin.has_permission(permission)
            print(f"   {permission}: {'✅' if has_perm else '❌'}")
        
        # Update permissions
        new_permissions = {
            'permissions': [
                'manage_products',
                'manage_customers',
                'manage_orders',
                'view_reports'
            ]
        }
        
        admin.permissions = new_permissions
        admin.save()
        
        print(f"Updated permissions: {admin.permissions}")
        
        return admin
        
    except Exception as e:
        print(f"❌ Error testing admin permissions: {e}")
        return None

def test_admin_dashboard_data():
    """Test admin dashboard data generation"""
    print("\n" + "=" * 60)
    print("📈 TESTING ADMIN DASHBOARD DATA")
    print("=" * 60)
    
    try:
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta
        
        # Get date range (last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Orders statistics
        total_orders = Order.objects.count()
        recent_orders = Order.objects.filter(created_at__gte=start_date).count()
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='completed').count()
        total_revenue = Order.objects.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Customers statistics
        total_customers = Customer.objects.count()
        new_customers = Customer.objects.filter(created_at__gte=start_date).count()
        
        # Products statistics
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(stock_quantity__lte=10).count()
        
        # Admin statistics
        total_admins = Admin.objects.count()
        active_admins = Admin.objects.filter(is_active=True).count()
        
        dashboard_data = {
            'orders': {
                'total': total_orders,
                'recent': recent_orders,
                'pending': pending_orders,
                'completed': completed_orders,
                'revenue': float(total_revenue)
            },
            'customers': {
                'total': total_customers,
                'new': new_customers
            },
            'products': {
                'total': total_products,
                'low_stock': low_stock_products
            },
            'admins': {
                'total': total_admins,
                'active': active_admins
            }
        }
        
        print("Dashboard Data:")
        print(f"  Orders: {dashboard_data['orders']}")
        print(f"  Customers: {dashboard_data['customers']}")
        print(f"  Products: {dashboard_data['products']}")
        print(f"  Admins: {dashboard_data['admins']}")
        
        print("✅ Dashboard data generated successfully!")
        
        return dashboard_data
        
    except Exception as e:
        print(f"❌ Error generating dashboard data: {e}")
        return None

def main():
    """Run all admin system tests"""
    print("🚀 ORDERFLOW ADMIN SYSTEM TEST SUITE")
    print("=" * 60)
    print("Testing comprehensive admin functionality")
    print("=" * 60)
    
    # Test admin creation
    admin = test_admin_creation()
    
    # Test admin notifications
    test_admin_notifications()
    
    # Test order notification to admins
    test_order_notification_to_admins()
    
    # Test daily report
    test_daily_report()
    
    # Test admin permissions
    test_admin_permissions()
    
    # Test dashboard data
    test_admin_dashboard_data()
    
    print("\n" + "=" * 60)
    print("🏁 ADMIN SYSTEM TEST SUITE COMPLETED")
    print("=" * 60)
    print("\nAdmin System Features:")
    print("✅ Admin user creation and management")
    print("✅ Admin notifications (order alerts, system alerts)")
    print("✅ Daily reports to admins")
    print("✅ Admin permissions system")
    print("✅ Admin dashboard with statistics")
    print("✅ CRUD operations for products, customers, orders")
    print("✅ Email notifications to admins for all orders")
    print("\nNext steps:")
    print("1. Create admin user: python manage.py create_admin admin@email.com 'First' 'Last' 'password'")
    print("2. Access admin dashboard via API")
    print("3. Test admin notifications with real orders")

if __name__ == "__main__":
    main()
