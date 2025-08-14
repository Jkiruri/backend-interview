from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .notification_manager import NotificationManager
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """
    Send notifications when order is created or status changes
    """
    notification_manager = NotificationManager()
    
    try:
        if created:
            # New order - send confirmation
            logger.info(f"Sending order confirmation for new order {instance.order_number}")
            result = notification_manager.send_order_confirmation(instance)
            
            if result['success']:
                logger.info(f"Order confirmation sent successfully for order {instance.order_number}")
            else:
                logger.error(f"Failed to send order confirmation for order {instance.order_number}")
        
        else:
            # Existing order - check if status changed
            if instance.tracker.has_changed('status'):
                old_status = instance.tracker.previous('status')
                new_status = instance.status
                
                logger.info(f"Order status changed from {old_status} to {new_status} for order {instance.order_number}")
                
                # Send status update notification
                result = notification_manager.send_order_status_update(instance, old_status, new_status)
                
                if result['success']:
                    logger.info(f"Status update notification sent successfully for order {instance.order_number}")
                else:
                    logger.error(f"Failed to send status update for order {instance.order_number}")
                
                # Send delivery notification if status is 'delivered'
                if new_status == 'delivered':
                    logger.info(f"Sending delivery notification for order {instance.order_number}")
                    delivery_result = notification_manager.send_delivery_notification(instance)
                    
                    if delivery_result['success']:
                        logger.info(f"Delivery notification sent successfully for order {instance.order_number}")
                    else:
                        logger.error(f"Failed to send delivery notification for order {instance.order_number}")
    
    except Exception as e:
        logger.error(f"Error in order notification signal for order {instance.order_number}: {e}")

