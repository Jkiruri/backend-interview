from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from customers.models import Admin, Customer
from .models import Notification
import logging

logger = logging.getLogger(__name__)

class AdminService:
    """Service for managing admin notifications and system operations"""
    
    def __init__(self):
        self.from_email = settings.EMAIL_HOST_USER
    
    def get_active_admins(self):
        """Get all active admin users"""
        return Admin.objects.filter(is_active=True, user__is_active=True)
    
    def get_admin_emails(self):
        """Get all active admin email addresses"""
        return [admin.user.email for admin in self.get_active_admins()]
    
    def send_admin_notification(self, subject, message, notification_type='admin', order=None):
        """
        Send notification to all active admins
        
        Args:
            subject (str): Email subject
            message (str): Email message
            notification_type (str): Type of notification
            order (Order): Optional order object for context
            
        Returns:
            dict: Results of sending notifications
        """
        admin_emails = self.get_admin_emails()
        
        if not admin_emails:
            logger.warning("No active admin emails found")
            return {
                'success': False,
                'error': 'No active admin emails found'
            }
        
        results = []
        success_count = 0
        
        for admin_email in admin_emails:
            try:
                # Send email
                result = send_mail(
                    subject=subject,
                    message=message,
                    from_email=self.from_email,
                    recipient_list=[admin_email],
                    fail_silently=False
                )
                
                if result:
                    success_count += 1
                    logger.info(f"Admin notification sent to {admin_email}")
                    
                    # Create notification record
                    admin = Admin.objects.get(user__email=admin_email)
                    Notification.objects.create(
                        notification_type='email',
                        recipient=admin.user,
                        order=order,
                        subject=subject,
                        message=message,
                        status='sent',
                        sent_at=timezone.now()
                    )
                else:
                    logger.error(f"Failed to send admin notification to {admin_email}")
                
                results.append({
                    'email': admin_email,
                    'success': bool(result)
                })
                
            except Exception as e:
                logger.error(f"Error sending admin notification to {admin_email}: {e}")
                results.append({
                    'email': admin_email,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'success': success_count > 0,
            'total_admins': len(admin_emails),
            'success_count': success_count,
            'results': results
        }
    
    def send_order_notification_to_admins(self, order):
        """
        Send order notification to all admins
        
        Args:
            order (Order): Order object
            
        Returns:
            dict: Results of sending notifications
        """
        subject = f"New Order Received - #{order.order_number}"
        
        message = f"""
Dear Administrator,

A new order has been placed with the following details:

Order Information:
- Order Number: {order.order_number}
- Customer: {order.customer.full_name}
- Customer Email: {order.customer.email}
- Customer Phone: {order.customer.phone_number}
- Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}
- Order Status: {order.status.title()}
- Total Amount: Ksh {order.total_amount}

Order Items:
{self._format_order_items(order)}

Customer Information:
- Name: {order.customer.full_name}
- Email: {order.customer.email}
- Phone: {order.customer.phone_number}
- Address: {order.customer.address}

Shipping Address:
{order.shipping_address}

Billing Address:
{order.billing_address}

Payment Information:
- Payment Method: {order.payment_method}
- Payment Status: {'Paid' if order.is_paid else 'Pending'}

Notes: {order.notes}

Please process this order accordingly.

Best regards,
OrderFlow System
        """.strip()
        
        return self.send_admin_notification(subject, message, 'order_notification', order)
    
    def send_system_alert_to_admins(self, alert_type, message, details=None):
        """
        Send system alert to all admins
        
        Args:
            alert_type (str): Type of alert (error, warning, info)
            message (str): Alert message
            details (dict): Additional details
            
        Returns:
            dict: Results of sending notifications
        """
        subject = f"System Alert - {alert_type.upper()}"
        
        alert_message = f"""
Dear Administrator,

System Alert: {alert_type.upper()}

Message: {message}

Time: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}

{f'Details: {details}' if details else ''}

Please review and take appropriate action.

Best regards,
OrderFlow System
        """.strip()
        
        return self.send_admin_notification(subject, alert_message, 'system_alert')
    
    def send_daily_report_to_admins(self, report_data):
        """
        Send daily report to all admins
        
        Args:
            report_data (dict): Report data
            
        Returns:
            dict: Results of sending notifications
        """
        subject = f"Daily Report - {timezone.now().strftime('%B %d, %Y')}"
        
        message = f"""
Dear Administrator,

Daily System Report for {timezone.now().strftime('%B %d, %Y')}

Orders Summary:
- Total Orders: {report_data.get('total_orders', 0)}
- New Orders: {report_data.get('new_orders', 0)}
- Completed Orders: {report_data.get('completed_orders', 0)}
- Pending Orders: {report_data.get('pending_orders', 0)}
- Total Revenue: Ksh {report_data.get('total_revenue', 0)}

Customers Summary:
- Total Customers: {report_data.get('total_customers', 0)}
- New Customers: {report_data.get('new_customers', 0)}

Products Summary:
- Total Products: {report_data.get('total_products', 0)}
- Low Stock Items: {report_data.get('low_stock_items', 0)}

System Health:
- Notifications Sent: {report_data.get('notifications_sent', 0)}
- Failed Notifications: {report_data.get('failed_notifications', 0)}
- System Uptime: {report_data.get('system_uptime', 'N/A')}

Best regards,
OrderFlow System
        """.strip()
        
        return self.send_admin_notification(subject, message, 'daily_report')
    
    def _format_order_items(self, order):
        """Format order items for email"""
        items_text = ""
        for item in order.items.all():
            items_text += f"- {item.product.name} x{item.quantity} @ Ksh {item.unit_price} = Ksh {item.quantity * item.unit_price}\n"
        return items_text
    
    def create_admin_user(self, email, first_name, last_name, password, role='admin', permissions=None):
        """
        Create a new admin user
        
        Args:
            email (str): Admin email
            first_name (str): First name
            last_name (str): Last name
            password (str): Password
            role (str): Admin role
            permissions (dict): Admin permissions
            
        Returns:
            Admin: Created admin object
        """
        try:
            # Create customer user
            customer = Customer.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                is_staff=True,
                is_superuser=True,
                is_verified=True,
                is_active=True
            )
            
            # Create admin profile
            admin = Admin.objects.create(
                user=customer,
                role=role,
                permissions=permissions or {},
                is_active=True
            )
            
            logger.info(f"Created admin user: {email}")
            return admin
            
        except Exception as e:
            logger.error(f"Error creating admin user {email}: {e}")
            raise
    
    def update_admin_permissions(self, admin_id, permissions):
        """
        Update admin permissions
        
        Args:
            admin_id (str): Admin UUID
            permissions (dict): New permissions
            
        Returns:
            Admin: Updated admin object
        """
        try:
            admin = Admin.objects.get(id=admin_id)
            admin.permissions = permissions
            admin.save()
            
            logger.info(f"Updated permissions for admin: {admin.email}")
            return admin
            
        except Admin.DoesNotExist:
            logger.error(f"Admin not found: {admin_id}")
            raise
        except Exception as e:
            logger.error(f"Error updating admin permissions: {e}")
            raise
    
    def deactivate_admin(self, admin_id):
        """
        Deactivate an admin user
        
        Args:
            admin_id (str): Admin UUID
            
        Returns:
            Admin: Deactivated admin object
        """
        try:
            admin = Admin.objects.get(id=admin_id)
            admin.is_active = False
            admin.user.is_active = False
            admin.user.save()
            admin.save()
            
            logger.info(f"Deactivated admin: {admin.email}")
            return admin
            
        except Admin.DoesNotExist:
            logger.error(f"Admin not found: {admin_id}")
            raise
        except Exception as e:
            logger.error(f"Error deactivating admin: {e}")
            raise
