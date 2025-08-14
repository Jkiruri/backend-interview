from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Notification, EmailNotification
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.from_email = settings.EMAIL_HOST_USER
        self.fail_silently = False
    
    def send_email(self, to_email, subject, message, notification_id=None, html_message=None):
        """
        Send email notification
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            message (str): Email message content
            notification_id (str): Optional notification ID for tracking
            html_message (str): Optional HTML version of the message
            
        Returns:
            dict: Response with status and details
        """
        try:
            # Send email
            result = send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[to_email],
                fail_silently=self.fail_silently,
                html_message=html_message
            )
            
            if result:
                # Update notification if ID provided
                if notification_id:
                    self._update_notification(notification_id, 'sent')
                
                return {
                    'success': True,
                    'status': 'sent'
                }
            else:
                # Update notification if ID provided
                if notification_id:
                    self._update_notification(notification_id, 'failed', 'Email sending failed')
                
                return {
                    'success': False,
                    'error': 'Email sending failed'
                }
                
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            
            # Update notification if ID provided
            if notification_id:
                self._update_notification(notification_id, 'failed', str(e))
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_notification(self, notification_id, status, error_message=''):
        """Update notification record with email details"""
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.status = status
            notification.sent_at = timezone.now()
            
            if error_message:
                notification.error_message = error_message
            
            notification.save()
            
            # Update email details
            email_notification, created = EmailNotification.objects.get_or_create(
                notification=notification,
                defaults={
                    'email_address': notification.recipient.email,
                    'template_used': 'custom'
                }
            )
            
            if not created:
                email_notification.save()
                
        except Exception as e:
            logger.error(f"Failed to update notification {notification_id}: {e}")
    
    def send_order_confirmation(self, order):
        """Send order confirmation email"""
        customer = order.customer
        
        # Create email content
        subject = f"Order Confirmation - #{order.order_number}"
        
        # Plain text message
        message = f"""
Dear {customer.first_name},

Thank you for your order! Your order has been confirmed.

Order Details:
- Order Number: {order.order_number}
- Total Amount: ${order.total_amount}
- Status: {order.status.title()}
- Date: {order.created_at.strftime('%B %d, %Y')}

Order Items:
{self._format_order_items(order)}

Shipping Address:
{order.shipping_address}

We will keep you updated on your order status.

Thank you for shopping with us!

Best regards,
OrderFlow Team
        """.strip()
        
        # HTML message
        html_message = self._render_order_confirmation_html(order)
        
        # Create notification record
        notification = Notification.objects.create(
            notification_type='email',
            recipient=customer,
            order=order,
            subject=subject,
            message=message,
            status='pending'
        )
        
        # Send email
        result = self.send_email(
            customer.email,
            subject,
            message,
            str(notification.id),
            html_message
        )
        
        return result
    
    def send_order_status_update(self, order, old_status, new_status):
        """Send order status update email"""
        customer = order.customer
        
        subject = f"Order Status Update - #{order.order_number}"
        
        message = f"""
Dear {customer.first_name},

Your order status has been updated.

Order Details:
- Order Number: {order.order_number}
- Previous Status: {old_status.title()}
- New Status: {new_status.title()}
- Total Amount: ${order.total_amount}

You can track your order at our website.

Thank you for your patience!

Best regards,
OrderFlow Team
        """.strip()
        
        # Create notification record
        notification = Notification.objects.create(
            notification_type='email',
            recipient=customer,
            order=order,
            subject=subject,
            message=message,
            status='pending'
        )
        
        # Send email
        result = self.send_email(
            customer.email,
            subject,
            message,
            str(notification.id)
        )
        
        return result
    
    def send_delivery_notification(self, order):
        """Send delivery notification email"""
        customer = order.customer
        
        subject = f"Order Delivered - #{order.order_number}"
        
        message = f"""
Dear {customer.first_name},

Great news! Your order has been delivered.

Order Details:
- Order Number: {order.order_number}
- Total Amount: ${order.total_amount}
- Delivery Date: {timezone.now().strftime('%B %d, %Y')}

We hope you enjoy your purchase! If you have any questions or concerns, please don't hesitate to contact us.

Thank you for shopping with us!

Best regards,
OrderFlow Team
        """.strip()
        
        # Create notification record
        notification = Notification.objects.create(
            notification_type='email',
            recipient=customer,
            order=order,
            subject=subject,
            message=message,
            status='pending'
        )
        
        # Send email
        result = self.send_email(
            customer.email,
            subject,
            message,
            str(notification.id)
        )
        
        return result
    
    def _format_order_items(self, order):
        """Format order items for email"""
        items_text = ""
        for item in order.items.all():
            items_text += f"- {item.product.name} x{item.quantity} @ ${item.unit_price} = ${item.quantity * item.unit_price}\n"
        return items_text
    
    def _render_order_confirmation_html(self, order):
        """Render HTML version of order confirmation"""
        context = {
            'order': order,
            'customer': order.customer,
            'items': order.items.all()
        }
        
        try:
            return render_to_string('notifications/order_confirmation.html', context)
        except:
            # Fallback to simple HTML if template doesn't exist
            return f"""
            <html>
            <body>
                <h2>Order Confirmation</h2>
                <p>Dear {order.customer.first_name},</p>
                <p>Thank you for your order! Your order has been confirmed.</p>
                <h3>Order Details:</h3>
                <ul>
                    <li>Order Number: {order.order_number}</li>
                    <li>Total Amount: ${order.total_amount}</li>
                    <li>Status: {order.status.title()}</li>
                    <li>Date: {order.created_at.strftime('%B %d, %Y')}</li>
                </ul>
                <p>Thank you for shopping with us!</p>
                <p>Best regards,<br>OrderFlow Team</p>
            </body>
            </html>
            """

