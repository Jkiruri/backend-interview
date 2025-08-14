# OrderFlow - E-commerce Order Management System

A comprehensive Django-based order management system with hierarchical product categories, customer management, and automated notifications.

## Features

- **Hierarchical Product Categories**: Support for unlimited depth category organization
- **Customer Management**: Custom user model with email-based authentication
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
python setup_db.py

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
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
├── requirements.txt        # Python dependencies
├── setup_db.py            # Database setup script
├── env.example            # Environment variables template
└── README.md              # This file
```

## Database Schema

### Customers
- Custom user model extending Django's AbstractUser
- Email-based authentication
- Customer-specific fields (phone, address, etc.)

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
