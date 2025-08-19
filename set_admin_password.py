#!/usr/bin/env python3
"""
Script to set admin password
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.contrib.auth.models import User

def set_admin_password():
    """Set admin password"""
    print("=" * 60)
    print("🔐 SETTING ADMIN PASSWORD")
    print("=" * 60)
    
    try:
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin@jameskiruri.co.ke',
            defaults={
                'email': 'admin@jameskiruri.co.ke',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        # Set password
        admin_user.set_password('admin123456')
        admin_user.save()
        
        if created:
            print(f"✅ Created admin user: {admin_user.email}")
        else:
            print(f"✅ Updated admin user: {admin_user.email}")
        
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Name: {admin_user.get_full_name()}")
        print(f"   Is Staff: {admin_user.is_staff}")
        print(f"   Is Superuser: {admin_user.is_superuser}")
        print("   Password: admin123456")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error setting admin password: {e}")
        return None

def main():
    """Main function"""
    print("🚀 ADMIN PASSWORD SETUP")
    print("=" * 60)
    
    # Set admin password
    admin = set_admin_password()
    
    if admin:
        print("\n" + "=" * 60)
        print("🏁 ADMIN SETUP COMPLETED")
        print("=" * 60)
        print("\nAdmin Credentials:")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print("Password: admin123456")
        print("\nYou can now:")
        print("1. Login to Django Admin: http://localhost:8000/admin")
        print("2. Use this admin for system management")
        print("3. All orders will be sent to admin@jameskiruri.co.ke")
        print("4. Admin has full CRUD access to all models")

if __name__ == "__main__":
    main()
