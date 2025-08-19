from .sms_service import SMSService
from .email_service import EmailService
from .admin_service import AdminService
from .models import Notification
from .tasks import send_sms_notification, send_email_notification, send_order_confirmation, send_order_status_update
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages both SMS and email notifications using Celery tasks"""
    
    def __init__(self):
        self.sms_service = SMSService()
        self.email_service = EmailService()
        self.admin_service = AdminService()
    
    def send_order_confirmation(self, order, send_sms=True, send_email=True, send_admin_notification=True):
        """
        Send order confirmation notifications asynchronously using Celery
        
        Args:
            order: Order object
            send_sms (bool): Whether to send SMS
            send_email (bool): Whether to send email
            send_admin_notification (bool): Whether to send admin notification
            
        Returns:
            dict: Results with task IDs
        """
        try:
            # Queue the task asynchronously
            task_result = send_order_confirmation.delay(
                str(order.id), 
                send_sms=send_sms, 
                send_email=send_email
            )
            
            logger.info(f"Order confirmation task queued for order {order.order_number} - Task ID: {task_result.id}")
            
            # Send admin notification immediately (not async)
            admin_result = None
            if send_admin_notification:
                admin_result = self.admin_service.send_order_notification_to_admins(order)
                logger.info(f"Admin notification sent for order {order.order_number}")
            
            return {
                'success': True,
                'task_id': task_result.id,
                'status': 'queued',
                'message': 'Order confirmation notifications queued successfully',
                'admin_notification': admin_result
            }
            
        except Exception as e:
            logger.error(f"Failed to queue order confirmation for order {order.order_number}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_order_status_update(self, order, old_status, new_status, send_sms=True, send_email=True):
        """
        Send order status update notifications asynchronously using Celery
        
        Args:
            order: Order object
            old_status (str): Previous order status
            new_status (str): New order status
            send_sms (bool): Whether to send SMS
            send_email (bool): Whether to send email
            
        Returns:
            dict: Results with task IDs
        """
        try:
            # Queue the task asynchronously
            task_result = send_order_status_update.delay(
                str(order.id), 
                old_status, 
                new_status, 
                send_sms=send_sms, 
                send_email=send_email
            )
            
            logger.info(f"Order status update task queued for order {order.order_number} - Task ID: {task_result.id}")
            
            return {
                'success': True,
                'task_id': task_result.id,
                'status': 'queued',
                'message': 'Order status update notifications queued successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to queue status update for order {order.order_number}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_delivery_notification(self, order, send_sms=True, send_email=True):
        """
        Send delivery notification
        
        Args:
            order: Order object
            send_sms (bool): Whether to send SMS
            send_email (bool): Whether to send email
            
        Returns:
            dict: Results from both services
        """
        results = {
            'sms': None,
            'email': None,
            'success': False
        }
        
        try:
            # Send SMS if enabled and customer has phone number
            if send_sms and order.customer.phone_number:
                results['sms'] = self.sms_service.send_delivery_notification(order)
                logger.info(f"SMS delivery notification sent for order {order.order_number}")
            
            # Send email if enabled
            if send_email:
                results['email'] = self.email_service.send_delivery_notification(order)
                logger.info(f"Email delivery notification sent for order {order.order_number}")
            
            # Consider successful if at least one notification was sent
            results['success'] = (
                (results['sms'] and results['sms'].get('success', False)) or
                (results['email'] and results['email'].get('success', False))
            )
            
        except Exception as e:
            logger.error(f"Failed to send delivery notification for order {order.order_number}: {e}")
            results['error'] = str(e)
        
        return results
    
    def send_custom_notification(self, customer, message, subject="", send_sms=True, send_email=True):
        """
        Send custom notification to a customer
        
        Args:
            customer: Customer object
            message (str): Message content
            subject (str): Email subject (for email notifications)
            send_sms (bool): Whether to send SMS
            send_email (bool): Whether to send email
            
        Returns:
            dict: Results from both services
        """
        results = {
            'sms': None,
            'email': None,
            'success': False
        }
        
        try:
            # Send SMS if enabled and customer has phone number
            if send_sms and customer.phone_number:
                results['sms'] = self.sms_service.send_sms(customer.phone_number, message)
                logger.info(f"Custom SMS sent to {customer.email}")
            
            # Send email if enabled
            if send_email:
                results['email'] = self.email_service.send_email(
                    customer.email, 
                    subject or "Notification from OrderFlow", 
                    message
                )
                logger.info(f"Custom email sent to {customer.email}")
            
            # Consider successful if at least one notification was sent
            results['success'] = (
                (results['sms'] and results['sms'].get('success', False)) or
                (results['email'] and results['email'].get('success', False))
            )
            
        except Exception as e:
            logger.error(f"Failed to send custom notification to {customer.email}: {e}")
            results['error'] = str(e)
        
        return results
    
    def get_notification_stats(self, customer=None):
        """
        Get notification statistics
        
        Args:
            customer: Optional customer to filter by
            
        Returns:
            dict: Notification statistics
        """
        queryset = Notification.objects.all()
        
        if customer:
            queryset = queryset.filter(recipient=customer)
        
        stats = {
            'total': queryset.count(),
            'sms': queryset.filter(notification_type='sms').count(),
            'email': queryset.filter(notification_type='email').count(),
            'pending': queryset.filter(status='pending').count(),
            'sent': queryset.filter(status='sent').count(),
            'failed': queryset.filter(status='failed').count(),
            'delivered': queryset.filter(status='delivered').count(),
        }
        
        return stats

