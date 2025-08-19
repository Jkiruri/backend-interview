from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .tasks import send_order_status_update, send_delivery_notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    """
    Handle order status changes (not creation)
    Order creation notifications are handled in the serializer
    """
    if not created and hasattr(instance, 'tracker') and instance.tracker.has_changed('status'):
        old_status = instance.tracker.previous('status')
        new_status = instance.status
        
        logger.info(f"Queueing status update for order {instance.order_number}: {old_status} → {new_status}")
        
        try:
            # Queue status update notifications
            status_task = send_order_status_update.delay(
                str(instance.id), 
                old_status, 
                new_status, 
                send_sms=True, 
                send_email=True
            )
            
            logger.info(f"Status update task queued for order {instance.order_number} - Task ID: {status_task.id}")
            
            # Queue delivery notification if status is 'delivered'
            if new_status == 'delivered':
                logger.info(f"Queueing delivery notification for order {instance.order_number}")
                delivery_task = send_delivery_notification.delay(str(instance.id))
                logger.info(f"Delivery notification task queued - Task ID: {delivery_task.id}")
                
        except Exception as e:
            logger.error(f"Error queueing status update for order {instance.order_number}: {e}")

