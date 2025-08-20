# Database Seeders

This directory contains database seeding scripts for the OrderFlow project.

## Scripts Overview

### `seeders.py`
- **Purpose**: Populate database with realistic test data
- **Usage**: `python seeder/seeders.py`
- **Description**: Creates sample customers, products, categories, and orders for testing

### `create_admin_final.py`
- **Purpose**: Create admin user with comprehensive functionality
- **Usage**: `python seeder/create_admin_final.py`
- **Description**: Creates admin user, tests login, email notifications, and database connections

## Running Seeders

All seeders should be run from the project root directory:

```bash
# Run all seeders (customers, products, orders)
python seeder/seeders.py

# Create admin user with full functionality
python seeder/create_admin_final.py
```

## Admin Creation Features

The `create_admin_final.py` script includes:

- ✅ Admin user creation with Django User model
- ✅ Admin login testing
- ✅ Email notification testing
- ✅ Database connection testing
- ✅ Order notification testing
- ✅ Admin CRUD access testing

## Default Admin Credentials

- **Email**: admin@jameskiruri.co.ke
- **Password**: admin123456
- **Permissions**: Full staff and superuser access

## Notes

- All scripts automatically set up the Django environment
- Seeders are designed to be run multiple times safely (uses get_or_create)
- Admin creation script includes comprehensive testing and validation
