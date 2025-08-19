# OrderFlow Admin System Guide

## Overview

The OrderFlow Admin System provides comprehensive administrative capabilities for managing the e-commerce platform. This guide covers setup, configuration, and usage of all admin features.

## Table of Contents

1. [Admin Setup](#admin-setup)
2. [Admin Credentials](#admin-credentials)
3. [Admin Features](#admin-features)
4. [API Endpoints](#api-endpoints)
5. [Admin Dashboard](#admin-dashboard)
6. [Product Management](#product-management)
7. [Customer Management](#customer-management)
8. [Order Management](#order-management)
9. [System Management](#system-management)
10. [Notifications](#notifications)
11. [Troubleshooting](#troubleshooting)

## Admin Setup

### 1. Database Seeding (Recommended)

The admin user is automatically created when running the database seeder:

```bash
python seeder/seeders.py
```

This creates an admin user with the following credentials:
- **Email**: `admin@jameskiruri.co.ke`
- **Password**: `admin123456`

### 2. Manual Creation

Alternatively, create an admin user manually:

```bash
python manage.py createsuperuser
```

Then create the admin profile:

```python
python manage.py shell

from customers.models import Customer, Admin
from django.contrib.auth import get_user_model

Customer = get_user_model()
admin_user = Customer.objects.get(email='admin@jameskiruri.co.ke')
Admin.objects.create(
    user=admin_user,
    role='admin',
    permissions=['all'],
    is_active=True
)
```

### 3. Custom Management Command

Use the custom management command:

```bash
python manage.py create_admin
```

## Admin Credentials

### Default Admin User
- **Email**: `admin@jameskiruri.co.ke`
- **Password**: `admin123456`
- **Role**: Super Admin
- **Permissions**: All permissions

### Test Customer Users (from seeder)
- `john.doe@example.com` / `password123`
- `jane.smith@example.com` / `password123`
- `mike.wilson@example.com` / `password123`
- `sarah.jones@example.com` / `password123`
- `david.brown@example.com` / `password123`

## Admin Features

### Core Capabilities
- ✅ **Full CRUD Operations**: Products, Categories, Customers, Orders
- ✅ **Dashboard Analytics**: Sales, orders, customer statistics
- ✅ **Order Management**: Status updates, tracking, fulfillment
- ✅ **Customer Management**: Verification, deactivation, profile management
- ✅ **System Administration**: User management, alerts, reports
- ✅ **Notification System**: Email notifications for all orders
- ✅ **Asynchronous Processing**: RabbitMQ + Celery for background tasks

### Assessment Requirements Met
- ✅ **Send customer SMS**: Africa's Talking integration
- ✅ **Send administrator email**: All orders sent to admin@jameskiruri.co.ke
- ✅ **Asynchronous processing**: RabbitMQ + Celery implementation
- ✅ **Error handling**: Retry logic and monitoring
- ✅ **Admin system**: Complete CRUD and management capabilities

## API Endpoints

### Authentication
```
POST /v1/auth/login/
POST /v1/auth/register/
```

### Admin Dashboard
```
GET /v1/admin/dashboard/
GET /v1/admin/dashboard/recent-orders/
GET /v1/admin/dashboard/sales-analytics/
```

### Product Management (Admin)
```
GET /v1/admin/products/
POST /v1/admin/products/
PUT /v1/admin/products/{id}/
DELETE /v1/admin/products/{id}/
```

### Customer Management (Admin)
```
GET /v1/admin/customers/
GET /v1/admin/customers/{id}/
POST /v1/admin/customers/{id}/verify/
POST /v1/admin/customers/{id}/deactivate/
```

### Order Management (Admin)
```
GET /v1/admin/orders/
GET /v1/admin/orders/{id}/
PATCH /v1/admin/orders/{id}/
```

### System Management
```
POST /v1/admin/create-admin/
POST /v1/admin/send-alert/
GET /v1/admin/daily-report/
```

## Admin Dashboard

### Dashboard Statistics
The admin dashboard provides real-time statistics:

```json
{
  "total_orders": 150,
  "total_customers": 45,
  "total_products": 20,
  "total_revenue": "Ksh 25,000.00",
  "recent_orders": [...],
  "top_products": [...],
  "sales_analytics": {...}
}
```

### Recent Orders
View the latest orders with customer details and status:

```json
{
  "orders": [
    {
      "id": 1,
      "order_number": "ORD-20250814-0014",
      "customer": "John Doe",
      "total_amount": "Ksh 99.98",
      "status": "pending",
      "created_at": "2025-08-14T15:12:21Z"
    }
  ]
}
```

### Sales Analytics
Track sales performance over time:

```json
{
  "daily_sales": [...],
  "monthly_sales": [...],
  "top_categories": [...],
  "revenue_trends": {...}
}
```

## Product Management

### Create Product
```bash
curl -X POST http://localhost:8000/v1/admin/products/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Product description",
    "price": "99.99",
    "category": "category_id",
    "sku": "NEW-PROD-001",
    "stock_quantity": 100
  }'
```

### Update Product
```bash
curl -X PUT http://localhost:8000/v1/admin/products/{product_id}/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Product Name",
    "price": "149.99",
    "stock_quantity": 75
  }'
```

### Delete Product
```bash
curl -X DELETE http://localhost:8000/v1/admin/products/{product_id}/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN"
```

## Customer Management

### View All Customers
```bash
curl -X GET http://localhost:8000/v1/admin/customers/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN"
```

### Verify Customer
```bash
curl -X POST http://localhost:8000/v1/admin/customers/{customer_id}/verify/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN"
```

### Deactivate Customer
```bash
curl -X POST http://localhost:8000/v1/admin/customers/{customer_id}/deactivate/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN"
```

## Order Management

### View All Orders
```bash
curl -X GET http://localhost:8000/v1/admin/orders/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN"
```

### Update Order Status
```bash
curl -X PATCH http://localhost:8000/v1/admin/orders/{order_id}/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "shipped"
  }'
```

### Order Status Options
- `pending`: Order received, awaiting confirmation
- `confirmed`: Order confirmed, payment received
- `processing`: Order being prepared for shipment
- `shipped`: Order shipped, tracking available
- `delivered`: Order delivered to customer
- `cancelled`: Order cancelled

## System Management

### Create New Admin User
```bash
curl -X POST http://localhost:8000/v1/admin/create-admin/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newadmin@example.com",
    "password": "admin123456",
    "first_name": "New",
    "last_name": "Admin",
    "role": "admin",
    "permissions": ["products", "orders"]
  }'
```

### Send System Alert
```bash
curl -X POST http://localhost:8000/v1/admin/send-alert/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "System Maintenance Notice",
    "message": "System will be under maintenance from 2-4 AM",
    "alert_type": "maintenance"
  }'
```

### Get Daily Report
```bash
curl -X GET http://localhost:8000/v1/admin/daily-report/ \
  -H "Authorization: Token YOUR_ADMIN_TOKEN"
```

## Notifications

### Admin Email Notifications
All orders automatically trigger email notifications to `admin@jameskiruri.co.ke`:

- **Order Confirmation**: When a new order is placed
- **Status Updates**: When order status changes
- **Delivery Notifications**: When orders are delivered
- **System Alerts**: Maintenance notices and system updates

### Email Template Example
```
Subject: New Order Received - #ORD-20250814-0014

Dear Administrator,

A new order has been placed with the following details:

Order Information:
- Order Number: ORD-20250814-0014
- Customer: John Doe
- Order Date: August 14, 2025 at 3:12 PM
- Order Status: Pending
- Total Amount: Ksh 99.98

Please process this order accordingly.

Best regards,
OrderFlow System
```

### SMS Notifications
Customers receive SMS notifications via Africa's Talking:

```
Order #ORD-20250814-0014 confirmed!
Total: Ksh 99.98
Status: Pending
Thank you for your order!
```

## Postman Collection

Import the provided `OrderFlow_API_Collection.json` into Postman for easy API testing.

### Setup Variables
1. Set `base_url` to your server URL (e.g., `http://localhost:8000`)
2. Get admin token by logging in with admin credentials
3. Set `admin_token` variable with the received token
4. Update other variables as needed (product_id, order_id, etc.)

### Testing Workflow
1. **Login as Admin**: Use "Admin Login" request
2. **Copy Token**: Copy the token from the response
3. **Set Variable**: Update `admin_token` variable in Postman
4. **Test Endpoints**: Use any admin endpoint with the token

## Troubleshooting

### Common Issues

#### 1. Admin User Not Found
```bash
# Check if admin exists
python manage.py shell
from customers.models import Customer
Customer.objects.filter(email='admin@jameskiruri.co.ke').exists()
```

#### 2. Permission Denied
- Ensure admin user has `is_staff=True` and `is_superuser=True`
- Check if Admin profile exists and is active
- Verify token is valid and not expired

#### 3. Email Notifications Not Working
```bash
# Test email configuration
python test_admin_email.py
```

#### 4. RabbitMQ/Celery Issues
```bash
# Start Celery workers
python manage.py start_celery_worker --queues=email,sms,notifications

# Check worker status
celery -A orderflow inspect active
```

### Debug Commands

#### Check Admin Status
```python
python manage.py shell

from customers.models import Customer, Admin
admin = Customer.objects.get(email='admin@jameskiruri.co.ke')
print(f"Staff: {admin.is_staff}")
print(f"Superuser: {admin.is_superuser}")
print(f"Admin Profile: {hasattr(admin, 'admin_profile')}")
```

#### Test Admin Permissions
```python
python manage.py shell

from customers.models import Customer
admin = Customer.objects.get(email='admin@jameskiruri.co.ke')
print(f"Can access products: {admin.has_perm('products.view_product')}")
print(f"Can access orders: {admin.has_perm('orders.view_order')}")
```

#### Verify Email Configuration
```python
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

result = send_mail(
    'Test Email',
    'This is a test email.',
    settings.EMAIL_HOST_USER,
    ['admin@jameskiruri.co.ke'],
    fail_silently=False
)
print(f"Email sent: {result}")
```

## Security Considerations

### Admin Access
- Use strong passwords for admin accounts
- Implement rate limiting on admin endpoints
- Log all admin actions for audit trails
- Use HTTPS in production

### Token Security
- Tokens expire after 24 hours by default
- Store tokens securely in client applications
- Implement token refresh mechanism
- Log token usage for security monitoring

### Data Protection
- Encrypt sensitive customer data
- Implement proper access controls
- Regular security audits
- GDPR compliance for customer data

## Performance Optimization

### Database Optimization
- Use database indexes for frequently queried fields
- Implement database connection pooling
- Regular database maintenance and cleanup

### Caching
- Cache frequently accessed data (products, categories)
- Use Redis for session storage
- Implement API response caching

### Asynchronous Processing
- Use Celery for background tasks
- Implement task queuing for heavy operations
- Monitor task performance and failures

## Monitoring and Logging

### Application Logs
- Monitor Django application logs
- Track API request/response times
- Log admin actions for audit trails

### Celery Monitoring
- Use Flower for Celery monitoring
- Monitor task success/failure rates
- Track queue lengths and processing times

### System Monitoring
- Monitor server resources (CPU, memory, disk)
- Track database performance
- Monitor external service integrations (SMS, Email)

## Conclusion

The OrderFlow Admin System provides a comprehensive solution for managing the e-commerce platform. With full CRUD capabilities, real-time analytics, and automated notifications, administrators can efficiently manage all aspects of the business.

### Key Benefits
- ✅ Complete system management
- ✅ Real-time analytics and reporting
- ✅ Automated customer and admin notifications
- ✅ Asynchronous processing for scalability
- ✅ Comprehensive API for integration
- ✅ Security and audit features

### Next Steps
1. Import the Postman collection
2. Set up admin credentials
3. Test all admin endpoints
4. Configure monitoring and alerts
5. Deploy to production environment

For additional support or questions, refer to the main project documentation or contact the development team.
