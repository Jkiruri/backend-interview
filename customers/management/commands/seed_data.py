from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from products.models import Category, Product
from customers.models import Customer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Starting database seeding...')
        
        try:
            with transaction.atomic():
                self.create_admin_user()
                self.create_categories()
                self.create_products()
                self.create_test_customers()
                
            self.stdout.write(
                self.style.SUCCESS('Successfully seeded database!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding database: {str(e)}')
            )
            logger.error(f'Database seeding failed: {str(e)}')

    def create_admin_user(self):
        """Create super admin user if it doesn't exist"""
        User = get_user_model()
        
        if not User.objects.filter(email='admin@orderflow.com').exists():
            # Create the superuser
            admin_user = User.objects.create_superuser(
                email='admin@orderflow.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(f'Created admin user: {admin_user.email}')
        else:
            admin_user = User.objects.get(email='admin@orderflow.com')
            self.stdout.write('Admin user already exists')
        
        # Create or update the Admin profile with super_admin role
        admin_profile, created = Admin.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'super_admin',
                'permissions': {
                    'permissions': [
                        'manage_products',
                        'manage_customers', 
                        'manage_orders',
                        'manage_admins',
                        'view_reports',
                        'send_notifications',
                        'create_admins'
                    ]
                },
                'is_active': True
            }
        )
        
        if not created:
            # Update existing admin profile to super_admin
            admin_profile.role = 'super_admin'
            admin_profile.is_active = True
            admin_profile.permissions = {
                'permissions': [
                    'manage_products',
                    'manage_customers', 
                    'manage_orders',
                    'manage_admins',
                    'view_reports',
                    'send_notifications',
                    'create_admins'
                ]
            }
            admin_profile.save()
            self.stdout.write(f'Updated admin profile to super_admin role')
        else:
            self.stdout.write(f'Created super admin profile for: {admin_user.email}')
        
        # Ensure the user is staff and superuser
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        self.stdout.write(f'Admin user {admin_user.email} is now super_admin with full permissions')

    def create_categories(self):
        """Create product categories"""
        categories_data = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and gadgets',
                'children': [
                    {
                        'name': 'Smartphones',
                        'description': 'Mobile phones and accessories',
                        'children': [
                            {'name': 'iPhone', 'description': 'Apple smartphones'},
                            {'name': 'Samsung', 'description': 'Samsung smartphones'},
                            {'name': 'Android', 'description': 'Other Android phones'},
                        ]
                    },
                    {
                        'name': 'Laptops',
                        'description': 'Portable computers',
                        'children': [
                            {'name': 'Gaming Laptops', 'description': 'High-performance gaming laptops'},
                            {'name': 'Business Laptops', 'description': 'Professional laptops'},
                            {'name': 'Student Laptops', 'description': 'Affordable laptops for students'},
                        ]
                    },
                    {
                        'name': 'Accessories',
                        'description': 'Electronic accessories',
                        'children': [
                            {'name': 'Chargers', 'description': 'Phone and laptop chargers'},
                            {'name': 'Cables', 'description': 'USB and other cables'},
                            {'name': 'Cases', 'description': 'Phone and laptop cases'},
                        ]
                    }
                ]
            },
            {
                'name': 'Clothing',
                'description': 'Fashion and apparel',
                'children': [
                    {
                        'name': 'Men\'s Clothing',
                        'description': 'Clothing for men',
                        'children': [
                            {'name': 'Shirts', 'description': 'Men\'s shirts and t-shirts'},
                            {'name': 'Pants', 'description': 'Men\'s pants and jeans'},
                            {'name': 'Shoes', 'description': 'Men\'s footwear'},
                        ]
                    },
                    {
                        'name': 'Women\'s Clothing',
                        'description': 'Clothing for women',
                        'children': [
                            {'name': 'Dresses', 'description': 'Women\'s dresses'},
                            {'name': 'Tops', 'description': 'Women\'s tops and blouses'},
                            {'name': 'Shoes', 'description': 'Women\'s footwear'},
                        ]
                    }
                ]
            },
            {
                'name': 'Home & Garden',
                'description': 'Home improvement and garden supplies',
                'children': [
                    {
                        'name': 'Furniture',
                        'description': 'Home furniture',
                        'children': [
                            {'name': 'Living Room', 'description': 'Living room furniture'},
                            {'name': 'Bedroom', 'description': 'Bedroom furniture'},
                            {'name': 'Kitchen', 'description': 'Kitchen furniture'},
                        ]
                    },
                    {
                        'name': 'Garden',
                        'description': 'Garden supplies and tools',
                        'children': [
                            {'name': 'Plants', 'description': 'Garden plants and flowers'},
                            {'name': 'Tools', 'description': 'Garden tools and equipment'},
                            {'name': 'Decorations', 'description': 'Garden decorations'},
                        ]
                    }
                ]
            }
        ]
        
        for category_data in categories_data:
            self.create_category_hierarchy(category_data)

    def create_category_hierarchy(self, category_data, parent=None):
        """Recursively create category hierarchy"""
        category, created = Category.objects.get_or_create(
            name=category_data['name'],
            defaults={
                'description': category_data['description'],
                'parent': parent
            }
        )
        
        if created:
            self.stdout.write(f'Created category: {category.name}')
        
        # Create child categories
        for child_data in category_data.get('children', []):
            self.create_category_hierarchy(child_data, category)

    def create_products(self):
        """Create sample products"""
        products_data = [
            {
                'name': 'iPhone 15 Pro',
                'description': 'Latest iPhone with advanced features',
                'price': 999.99,
                'category_name': 'iPhone',
                'stock_quantity': 50
            },
            {
                'name': 'Samsung Galaxy S24',
                'description': 'Premium Android smartphone',
                'price': 899.99,
                'category_name': 'Samsung',
                'stock_quantity': 45
            },
            {
                'name': 'MacBook Pro 16"',
                'description': 'Professional laptop for developers',
                'price': 2499.99,
                'category_name': 'Business Laptops',
                'stock_quantity': 20
            },
            {
                'name': 'Gaming Laptop RTX 4080',
                'description': 'High-performance gaming laptop',
                'price': 1899.99,
                'category_name': 'Gaming Laptops',
                'stock_quantity': 15
            },
            {
                'name': 'USB-C Charger',
                'description': 'Fast charging USB-C cable',
                'price': 19.99,
                'category_name': 'Chargers',
                'stock_quantity': 100
            },
            {
                'name': 'Men\'s Casual Shirt',
                'description': 'Comfortable casual shirt for men',
                'price': 29.99,
                'category_name': 'Shirts',
                'stock_quantity': 75
            },
            {
                'name': 'Women\'s Summer Dress',
                'description': 'Elegant summer dress',
                'price': 59.99,
                'category_name': 'Dresses',
                'stock_quantity': 40
            },
            {
                'name': 'Living Room Sofa',
                'description': 'Comfortable 3-seater sofa',
                'price': 599.99,
                'category_name': 'Living Room',
                'stock_quantity': 10
            }
        ]
        
        for product_data in products_data:
            try:
                category = Category.objects.get(name=product_data['category_name'])
                product, created = Product.objects.get_or_create(
                    name=product_data['name'],
                    defaults={
                        'description': product_data['description'],
                        'price': product_data['price'],
                        'category': category,
                        'stock_quantity': product_data['stock_quantity']
                    }
                )
                
                if created:
                    self.stdout.write(f'Created product: {product.name}')
                    
            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Category not found: {product_data["category_name"]}')
                )

    def create_test_customers(self):
        """Create test customers"""
        customers_data = [
            {
                'email': 'john.doe@example.com',
                'password': 'testpass123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '+254700000001'
            },
            {
                'email': 'jane.smith@example.com',
                'password': 'testpass123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '+254700000002'
            },
            {
                'email': 'bob.wilson@example.com',
                'password': 'testpass123',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'phone': '+254700000003'
            }
        ]
        
        for customer_data in customers_data:
            if not Customer.objects.filter(email=customer_data['email']).exists():
                customer = Customer.objects.create_user(
                    email=customer_data['email'],
                    password=customer_data['password'],
                    first_name=customer_data['first_name'],
                    last_name=customer_data['last_name'],
                    phone_number=customer_data['phone']
                )
                self.stdout.write(f'Created customer: {customer.email}')
            else:
                self.stdout.write(f'Customer already exists: {customer_data["email"]}')
