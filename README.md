# OrderFlow - E-commerce Order Management System

A comprehensive Django-based order management system with hierarchical product categories, customer management, and automated notifications.

## Features

- **Hierarchical Product Categories**: Support for unlimited depth category organization
- **Customer Management**: Custom user model with email-based authentication
- **OpenID Connect Authentication**: Primary authentication method as required by assessment
- **Order Processing**: Complete order lifecycle management
- **RESTful API**: Full-featured API with Django REST Framework
- **Database**: PostgreSQL with proper relationships and constraints
- **Testing**: Comprehensive test suite with coverage reporting

## Tech Stack

- **Backend**: Django 5.2.5, Django REST Framework
- **Database**: PostgreSQL
- **Testing**: pytest, coverage
- **Documentation**: drf-yasg (Swagger/OpenAPI)

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Git

## Quick Start

### 1. Clone the Repository
```bash
git clone "https://github.com/Jkiruri/backend-interview"
cd backend-interview
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy the environment template and configure your settings:
```bash
cp env.example .env
# Edit .env with your configuration
```

### 5. Database Setup
```bash
# Create PostgreSQL database
python scripts/setup_db.py

# Run migrations
python manage.py migrate

# Create admin user (optional)
python seeder/create_admin_final.py
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Project Structure

```
backend-interview/
├── orderflow/              # Django project settings
├── customers/              # Customer management app
├── products/               # Product and category management
├── orders/                 # Order processing app
├── seeder/                 # Database seeding and admin creation
├── scripts/                # Utility scripts
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
└── README.md              # This file
```

## Database Schema

### Customers
- Custom user model extending Django's AbstractUser
- Multiple authentication methods:
  - **OpenID Connect (Primary)**: OIDC provider integration
  - **Email-based authentication**: Traditional login
- Customer-specific fields (phone, address, etc.)
- Automatic user creation from OIDC claims

### Categories
- Hierarchical structure with unlimited depth
- Parent-child relationships
- Category paths and level tracking

### Products
- Product information with pricing
- Category associations
- Stock management
- SKU generation

### Orders
- Order lifecycle management
- Order items with quantities and pricing
- Status tracking
- Payment integration

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - Customer registration
- `POST /api/v1/auth/login/` - Customer login
- `POST /api/v1/auth/logout/` - Customer logout
- `POST /api/v1/auth/token/` - Get authentication token

### OpenID Connect
- `GET /api/v1/auth/oidc/login/` - Initiate OIDC login flow
- `POST /api/v1/auth/oidc/token/` - Exchange OIDC tokens for API tokens
- `GET /api/v1/auth/oidc/userinfo/` - Get OIDC user information

### Categories
- `GET /api/v1/categories/` - List categories
- `POST /api/v1/categories/` - Create category
- `GET /api/v1/categories/tree/` - Get category hierarchy
- `GET /api/v1/categories/{id}/average_price/` - Get average price for category

### Products
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product
- `POST /api/v1/products/upload/` - Upload product with image
- `GET /api/v1/products/featured/` - Get featured products
- `GET /api/v1/products/low_stock/` - Get low stock products

### Orders
- `GET /api/v1/orders/` - List orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/my_orders/` - Get user's orders
- `POST /api/v1/orders/{id}/update_status/` - Update order status
- `POST /api/v1/orders/{id}/cancel/` - Cancel order

### Customer Profile
- `GET /api/v1/customers/profile/` - Get user profile
- `PUT /api/v1/customers/update_profile/` - Update profile
- `POST /api/v1/customers/change_password/` - Change password

## Project Organization

### Scripts Directory (`scripts/`)
Contains utility scripts for project maintenance:
- `check_celery_status.py` - Monitor Celery workers and tasks
- `set_admin_password.py` - Set or update admin user credentials
- `setup_db.py` - Database initialization and setup

### Seeder Directory (`seeder/`)
Contains database seeding and admin creation scripts:
- `seeders.py` - Populate database with test data (customers, products, orders)
- `create_admin_final.py` - Create admin user with comprehensive testing

### Usage Examples
```bash
# Check Celery status
python scripts/check_celery_status.py

# Set admin password
python scripts/set_admin_password.py

# Create admin user with full functionality
python seeder/create_admin_final.py

# Populate database with test data
python seeder/seeders.py
```

## Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Documentation

API documentation is available at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
