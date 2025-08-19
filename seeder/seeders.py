#!/usr/bin/env python
"""
Database seeders for OrderFlow project
Populates the database with realistic test data
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orderflow.settings')
django.setup()

from django.contrib.auth import get_user_model
from customers.models import Customer, Admin
from products.models import Category, Product
from orders.models import Order, OrderItem
from django.core.files.uploadedfile import SimpleUploadedFile

Customer = get_user_model()

def create_customers():
    """Create sample customers"""
    print("Creating customers...")
    
    customers_data = [
        {
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+254700123456',
            'address': '123 Main St, Nairobi, Kenya',
            'city': 'Nairobi',
            'state': 'Nairobi',
            'country': 'Kenya',
            'postal_code': '00100',
            'is_verified': True
        },
        {
            'email': 'jane.smith@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone_number': '+254700123457',
            'address': '456 Oak Ave, Mombasa, Kenya',
            'city': 'Mombasa',
            'state': 'Mombasa',
            'country': 'Kenya',
            'postal_code': '80100',
            'is_verified': True
        },
        {
            'email': 'mike.wilson@example.com',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'phone_number': '+254700123458',
            'address': '789 Pine Rd, Kisumu, Kenya',
            'city': 'Kisumu',
            'state': 'Kisumu',
            'country': 'Kenya',
            'postal_code': '40100',
            'is_verified': False
        },
        {
            'email': 'sarah.jones@example.com',
            'first_name': 'Sarah',
            'last_name': 'Jones',
            'phone_number': '+254700123459',
            'address': '321 Elm St, Nakuru, Kenya',
            'city': 'Nakuru',
            'state': 'Nakuru',
            'country': 'Kenya',
            'postal_code': '20100',
            'is_verified': True
        },
        {
            'email': 'david.brown@example.com',
            'first_name': 'David',
            'last_name': 'Brown',
            'phone_number': '+254700123460',
            'address': '654 Maple Dr, Eldoret, Kenya',
            'city': 'Eldoret',
            'state': 'Uasin Gishu',
            'country': 'Kenya',
            'postal_code': '30100',
            'is_verified': True
        }
    ]
    
    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        if created:
            customer.set_password('password123')
            customer.save()
            customers.append(customer)
            print(f"✅ Created customer: {customer.full_name}")
        else:
            customers.append(customer)
            print(f"⏭️  Customer already exists: {customer.full_name}")
    
    return customers

def create_admin():
    """Create admin user"""
    print("\nCreating admin user...")
    
    admin_data = {
        'email': 'admin@jameskiruri.co.ke',
        'first_name': 'Admin',
        'last_name': 'User',
        'phone_number': '+254747210136',
        'address': 'Admin Office, Nairobi, Kenya',
        'city': 'Nairobi',
        'state': 'Nairobi',
        'country': 'Kenya',
        'postal_code': '00100',
        'is_verified': True,
        'is_staff': True,
        'is_superuser': True
    }
    
    try:
        admin_user, created = Customer.objects.get_or_create(
            email=admin_data['email'],
            defaults=admin_data
        )
        
        if created:
            admin_user.set_password('admin123456')
            admin_user.save()
            print(f"✅ Created admin user: {admin_user.email}")
        else:
            # Update existing admin user
            admin_user.set_password('admin123456')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            print(f"⏭️  Updated existing admin user: {admin_user.email}")
        
        # Create Admin profile
        admin_profile, profile_created = Admin.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'permissions': ['all'],
                'is_active': True
            }
        )
        
        if profile_created:
            print(f"✅ Created admin profile for: {admin_user.email}")
        else:
            print(f"⏭️  Admin profile already exists for: {admin_user.email}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return None

def create_categories():
    """Create hierarchical product categories"""
    print("\nCreating categories...")
    
    # Root categories
    electronics = Category.objects.get_or_create(
        name='Electronics',
        slug='electronics',
        description='Electronic devices and accessories'
    )[0]
    
    clothing = Category.objects.get_or_create(
        name='Clothing',
        slug='clothing',
        description='Fashion and apparel'
    )[0]
    
    home_garden = Category.objects.get_or_create(
        name='Home & Garden',
        slug='home-garden',
        description='Home improvement and garden supplies'
    )[0]
    
    books = Category.objects.get_or_create(
        name='Books',
        slug='books',
        description='Books and educational materials'
    )[0]
    
    # Electronics subcategories
    smartphones = Category.objects.get_or_create(
        name='Smartphones',
        slug='smartphones',
        parent=electronics,
        description='Mobile phones and accessories'
    )[0]
    
    laptops = Category.objects.get_or_create(
        name='Laptops',
        slug='laptops',
        parent=electronics,
        description='Portable computers and accessories'
    )[0]
    
    accessories = Category.objects.get_or_create(
        name='Accessories',
        slug='accessories',
        parent=electronics,
        description='Electronic accessories and peripherals'
    )[0]
    
    # Clothing subcategories
    mens_clothing = Category.objects.get_or_create(
        name="Men's Clothing",
        slug='mens-clothing',
        parent=clothing,
        description="Men's fashion and apparel"
    )[0]
    
    womens_clothing = Category.objects.get_or_create(
        name="Women's Clothing",
        slug='womens-clothing',
        parent=clothing,
        description="Women's fashion and apparel"
    )[0]
    
    kids_clothing = Category.objects.get_or_create(
        name="Kids' Clothing",
        slug='kids-clothing',
        parent=clothing,
        description="Children's fashion and apparel"
    )[0]
    
    # Home & Garden subcategories
    furniture = Category.objects.get_or_create(
        name='Furniture',
        slug='furniture',
        parent=home_garden,
        description='Home and office furniture'
    )[0]
    
    garden_tools = Category.objects.get_or_create(
        name='Garden Tools',
        slug='garden-tools',
        parent=home_garden,
        description='Gardening tools and equipment'
    )[0]
    
    # Books subcategories
    fiction = Category.objects.get_or_create(
        name='Fiction',
        slug='fiction',
        parent=books,
        description='Fiction books and novels'
    )[0]
    
    non_fiction = Category.objects.get_or_create(
        name='Non-Fiction',
        slug='non-fiction',
        parent=books,
        description='Non-fiction books and educational materials'
    )[0]
    
    categories = {
        'electronics': electronics,
        'clothing': clothing,
        'home_garden': home_garden,
        'books': books,
        'smartphones': smartphones,
        'laptops': laptops,
        'accessories': accessories,
        'mens_clothing': mens_clothing,
        'womens_clothing': womens_clothing,
        'kids_clothing': kids_clothing,
        'furniture': furniture,
        'garden_tools': garden_tools,
        'fiction': fiction,
        'non_fiction': non_fiction
    }
    
    print("✅ Categories created successfully")
    return categories

def create_products(categories):
    """Create sample products"""
    print("\nCreating products...")
    
    products_data = [
        # Smartphones
        {
            'name': 'iPhone 15 Pro',
            'description': 'Latest iPhone with advanced camera system and A17 Pro chip',
            'price': Decimal('1299.99'),
            'category': categories['smartphones'],
            'sku': 'IPH15PRO-001',
            'stock_quantity': 50
        },
        {
            'name': 'Samsung Galaxy S24',
            'description': 'Premium Android smartphone with AI features',
            'price': Decimal('999.99'),
            'category': categories['smartphones'],
            'sku': 'SAMS24-001',
            'stock_quantity': 45
        },
        {
            'name': 'Google Pixel 8',
            'description': 'Google\'s flagship phone with excellent camera',
            'price': Decimal('699.99'),
            'category': categories['smartphones'],
            'sku': 'PIXEL8-001',
            'stock_quantity': 30
        },
        
        # Laptops
        {
            'name': 'MacBook Pro 14"',
            'description': 'Professional laptop with M3 chip',
            'price': Decimal('1999.99'),
            'category': categories['laptops'],
            'sku': 'MBP14-001',
            'stock_quantity': 25
        },
        {
            'name': 'Dell XPS 13',
            'description': 'Premium Windows laptop with InfinityEdge display',
            'price': Decimal('1299.99'),
            'category': categories['laptops'],
            'sku': 'DELLXPS13-001',
            'stock_quantity': 35
        },
        {
            'name': 'Lenovo ThinkPad X1',
            'description': 'Business laptop with excellent keyboard',
            'price': Decimal('1499.99'),
            'category': categories['laptops'],
            'sku': 'THINKPADX1-001',
            'stock_quantity': 20
        },
        
        # Accessories
        {
            'name': 'AirPods Pro',
            'description': 'Wireless earbuds with active noise cancellation',
            'price': Decimal('249.99'),
            'category': categories['accessories'],
            'sku': 'AIRPODSPRO-001',
            'stock_quantity': 100
        },
        {
            'name': 'Samsung T7 SSD',
            'description': '1TB portable SSD with USB 3.2',
            'price': Decimal('89.99'),
            'category': categories['accessories'],
            'sku': 'SAMSUNGT7-001',
            'stock_quantity': 75
        },
        
        # Men's Clothing
        {
            'name': 'Classic White T-Shirt',
            'description': 'Premium cotton t-shirt for everyday wear',
            'price': Decimal('29.99'),
            'category': categories['mens_clothing'],
            'sku': 'TSHIRT-M-001',
            'stock_quantity': 200
        },
        {
            'name': 'Denim Jeans',
            'description': 'Comfortable denim jeans with stretch',
            'price': Decimal('79.99'),
            'category': categories['mens_clothing'],
            'sku': 'JEANS-M-001',
            'stock_quantity': 150
        },
        
        # Women's Clothing
        {
            'name': 'Summer Dress',
            'description': 'Elegant summer dress with floral pattern',
            'price': Decimal('89.99'),
            'category': categories['womens_clothing'],
            'sku': 'DRESS-W-001',
            'stock_quantity': 80
        },
        {
            'name': 'Blouse',
            'description': 'Professional blouse for office wear',
            'price': Decimal('59.99'),
            'category': categories['womens_clothing'],
            'sku': 'BLOUSE-W-001',
            'stock_quantity': 120
        },
        
        # Furniture
        {
            'name': 'Office Chair',
            'description': 'Ergonomic office chair with lumbar support',
            'price': Decimal('299.99'),
            'category': categories['furniture'],
            'sku': 'CHAIR-OFFICE-001',
            'stock_quantity': 40
        },
        {
            'name': 'Coffee Table',
            'description': 'Modern coffee table with storage',
            'price': Decimal('199.99'),
            'category': categories['furniture'],
            'sku': 'TABLE-COFFEE-001',
            'stock_quantity': 25
        },
        
        # Garden Tools
        {
            'name': 'Garden Shovel',
            'description': 'Heavy-duty garden shovel for landscaping',
            'price': Decimal('39.99'),
            'category': categories['garden_tools'],
            'sku': 'SHOVEL-001',
            'stock_quantity': 60
        },
        {
            'name': 'Pruning Shears',
            'description': 'Professional pruning shears for gardening',
            'price': Decimal('24.99'),
            'category': categories['garden_tools'],
            'sku': 'SHEARS-001',
            'stock_quantity': 90
        },
        
        # Books
        {
            'name': 'The Great Gatsby',
            'description': 'Classic American novel by F. Scott Fitzgerald',
            'price': Decimal('12.99'),
            'category': categories['fiction'],
            'sku': 'BOOK-GATSBY-001',
            'stock_quantity': 200
        },
        {
            'name': 'Python Programming',
            'description': 'Comprehensive guide to Python programming',
            'price': Decimal('49.99'),
            'category': categories['non_fiction'],
            'sku': 'BOOK-PYTHON-001',
            'stock_quantity': 150
        }
    ]
    
    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            sku=data['sku'],
            defaults=data
        )
        if created:
            products.append(product)
            print(f"✅ Created product: {product.name} - ${product.price}")
        else:
            products.append(product)
            print(f"⏭️  Product already exists: {product.name}")
    
    return products

def create_orders(customers, products):
    """Create sample orders"""
    print("\nCreating orders...")
    
    order_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']
    
    # Create orders for each customer
    for customer in customers:
        # Create 1-3 orders per customer
        num_orders = random.randint(1, 3)
        
        for i in range(num_orders):
            # Random order date within last 30 days
            order_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            # Random status (weighted towards completed orders)
            status_weights = {
                'pending': 0.1,
                'confirmed': 0.15,
                'processing': 0.2,
                'shipped': 0.25,
                'delivered': 0.25,
                'cancelled': 0.05
            }
            status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
            
            order = Order.objects.create(
                customer=customer,
                status=status,
                shipping_address=customer.address,
                total_amount=Decimal('0.00'),  # Set default value
                created_at=order_date
            )
            
            # Add 1-4 items to each order
            num_items = random.randint(1, 4)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                unit_price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                # Update product stock
                product.stock_quantity = max(0, product.stock_quantity - quantity)
                product.save()
            
            # Calculate total amount using the model method
            order.calculate_total()
            order.save()
            
            print(f"✅ Created order #{order.order_number} for {customer.full_name} - Ksh {order.total_amount}")

def main():
    """Run all seeders"""
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    try:
        # Create customers
        customers = create_customers()
        
        # Create admin
        admin_user = create_admin()
        
        # Create categories
        categories = create_categories()
        
        # Create products
        products = create_products(categories)
        
        # Create orders
        create_orders(customers, products)
        
        print("\n" + "=" * 50)
        print("🎉 Database seeding completed successfully!")
        print(f"📊 Created:")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(categories)} categories")
        print(f"   - {len(products)} products")
        print(f"   - {Order.objects.count()} orders")
        print(f"   - {OrderItem.objects.count()} order items")
        
        print("\n🔑 Test credentials:")
        for customer in customers:
            print(f"   - {customer.email} / password123")
        
        if admin_user:
            print(f"\n👑 Admin credentials:")
            print(f"   - {admin_user.email} / admin123456")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
