from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Notification, SMSNotification, EmailNotification
from .sms_service import SMSService
from .email_service import EmailService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_notification(self, notification_id):
    """
    Send SMS notification asynchronously
    
    Args:
        notification_id (str): UUID of the notification to send
        
    Returns:
        dict: Result of SMS sending operation
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if notification.status == 'sent':
            logger.info(f"SMS notification {notification_id} already sent")
            return {'success': True, 'status': 'already_sent'}
        
        # Initialize SMS service
        sms_service = SMSService()
        
        # Send SMS
        result = sms_service.send_sms(
            notification.recipient.phone_number,
            notification.message,
            str(notification.id)
        )
        
        if result.get('success'):
            logger.info(f"SMS notification {notification_id} sent successfully")
            return result
        else:
            logger.error(f"SMS notification {notification_id} failed: {result.get('error')}")
            # Retry the task
            raise self.retry(countdown=60, max_retries=3)
            
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {'success': False, 'error': 'Notification not found'}
    except Exception as e:
        logger.error(f"Error sending SMS notification {notification_id}: {e}")
        raise self.retry(countdown=60, max_retries=3)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_notification(self, notification_id):
    """
    Send email notification asynchronously
    
    Args:
        notification_id (str): UUID of the notification to send
        
    Returns:
        dict: Result of email sending operation
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if notification.status == 'sent':
            logger.info(f"Email notification {notification_id} already sent")
            return {'success': True, 'status': 'already_sent'}
        
        # Initialize email service
        email_service = EmailService()
        
        # Send email
        result = email_service.send_email(
            notification.recipient.email,
            notification.subject,
            notification.message,
            str(notification.id)
        )
        
        if result.get('success'):
            logger.info(f"Email notification {notification_id} sent successfully")
            return result
        else:
            logger.error(f"Email notification {notification_id} failed: {result.get('error')}")
            # Retry the task
            raise self.retry(countdown=60, max_retries=3)
            
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
        return {'success': False, 'error': 'Notification not found'}
    except Exception as e:
        logger.error(f"Error sending email notification {notification_id}: {e}")
        raise self.retry(countdown=60, max_retries=3)

@shared_task
def send_order_confirmation(order_id, send_sms=True, send_email=True):
    """
    Send order confirmation notifications asynchronously
    
    Args:
        order_id (str): UUID of the order
        send_sms (bool): Whether to send SMS
        send_email (bool): Whether to send email
        
    Returns:
        dict: Results from both services
    """
    from orders.models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        results = {'sms': None, 'email': None, 'success': False}
        
        # Send SMS if enabled and customer has phone number
        if send_sms and order.customer.phone_number:
            sms_service = SMSService()
            sms_result = sms_service.send_order_confirmation(order)
            results['sms'] = sms_result
            
            if sms_result.get('success'):
                logger.info(f"SMS order confirmation sent for order {order.order_number}")
        
        # Send email if enabled
        if send_email:
            email_service = EmailService()
            email_result = email_service.send_order_confirmation(order)
            results['email'] = email_result
            
            if email_result.get('success'):
                logger.info(f"Email order confirmation sent for order {order.order_number}")
        
        # Consider successful if at least one notification was sent
        results['success'] = (
            (results['sms'] and results['sms'].get('success', False)) or
            (results['email'] and results['email'].get('success', False))
        )
        
        return results
        
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return {'error': 'Order not found'}
    except Exception as e:
        logger.error(f"Error sending order confirmation for order {order_id}: {e}")
        return {'error': str(e)}

@shared_task
def send_order_status_update(order_id, old_status, new_status, send_sms=True, send_email=True):
    """
    Send order status update notifications asynchronously
    
    Args:
        order_id (str): UUID of the order
        old_status (str): Previous order status
        new_status (str): New order status
        send_sms (bool): Whether to send SMS
        send_email (bool): Whether to send email
        
    Returns:
        dict: Results from both services
    """
    from orders.models import Order
    
    try:
        order = Order.objects.get(id=order_id)
        results = {'sms': None, 'email': None, 'success': False}
        
        # Send SMS if enabled and customer has phone number
        if send_sms and order.customer.phone_number:
            sms_service = SMSService()
            sms_result = sms_service.send_order_status_update(order, old_status, new_status)
            results['sms'] = sms_result
            
            if sms_result.get('success'):
                logger.info(f"SMS status update sent for order {order.order_number}")
        
        # Send email if enabled
        if send_email:
            email_service = EmailService()
            email_result = email_service.send_order_status_update(order, old_status, new_status)
            results['email'] = email_result
            
            if email_result.get('success'):
                logger.info(f"Email status update sent for order {order.order_number}")
        
        # Consider successful if at least one notification was sent
        results['success'] = (
            (results['sms'] and results['sms'].get('success', False)) or
            (results['email'] and results['email'].get('success', False))
        )
        
        return results
        
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return {'error': 'Order not found'}
    except Exception as e:
        logger.error(f"Error sending status update for order {order_id}: {e}")
        return {'error': str(e)}

@shared_task
def retry_failed_notifications():
    """
    Retry failed notifications that haven't exceeded max retries
    """
    try:
        # Get failed notifications that can be retried
        failed_notifications = Notification.objects.filter(
            status='failed',
            retry_count__lt=3,
            created_at__gte=timezone.now() - timedelta(hours=24)
        )
        
        retry_count = 0
        for notification in failed_notifications:
            if notification.notification_type == 'sms':
                send_sms_notification.delay(str(notification.id))
                retry_count += 1
            elif notification.notification_type == 'email':
                send_email_notification.delay(str(notification.id))
                retry_count += 1
        
        logger.info(f"Retried {retry_count} failed notifications")
        return {'retried_count': retry_count}
        
    except Exception as e:
        logger.error(f"Error retrying failed notifications: {e}")
        return {'error': str(e)}

@shared_task
def cleanup_failed_notifications():
    """
    Clean up old failed notifications that have exceeded max retries
    """
    try:
        # Delete notifications that have failed and exceeded max retries
        # or are older than 7 days
        old_failed_notifications = Notification.objects.filter(
            status='failed',
            created_at__lt=timezone.now() - timedelta(days=7)
        )
        
        count = old_failed_notifications.count()
        old_failed_notifications.delete()
        
        logger.info(f"Cleaned up {count} old failed notifications")
        return {'cleaned_count': count}
        
    except Exception as e:
        logger.error(f"Error cleaning up failed notifications: {e}")
        return {'error': str(e)}

@shared_task
def send_bulk_sms_notifications(notification_ids):
    """
    Send multiple SMS notifications in bulk
    
    Args:
        notification_ids (list): List of notification UUIDs
        
    Returns:
        dict: Results for all notifications
    """
    results = []
    
    for notification_id in notification_ids:
        result = send_sms_notification.delay(notification_id)
        results.append({
            'notification_id': notification_id,
            'task_id': result.id
        })
    
    return {'results': results, 'total_count': len(notification_ids)}

@shared_task
def send_bulk_email_notifications(notification_ids):
    """
    Send multiple email notifications in bulk
    
    Args:
        notification_ids (list): List of notification UUIDs
        
    Returns:
        dict: Results for all notifications
    """
    results = []
    
    for notification_id in notification_ids:
        result = send_email_notification.delay(notification_id)
        results.append({
            'notification_id': notification_id,
            'task_id': result.id
        })
    
    return {'results': results, 'total_count': len(notification_ids)}

