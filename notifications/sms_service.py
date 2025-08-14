import africastalking
from django.conf import settings
from django.utils import timezone
from .models import Notification, SMSNotification
import logging

logger = logging.getLogger(__name__)

class SMSService:
    """SMS service using Africa's Talking"""
    
    def __init__(self):
        self.username = settings.AFRICASTALKING_USERNAME
        self.api_key = settings.AFRICASTALKING_API_KEY
        self.sender_id = settings.AFRICASTALKING_SENDER_ID
        
        # Initialize Africa's Talking SMS
        try:
            self.sms = africastalking.SMSService(self.username, self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Africa's Talking SMS: {e}")
            self.sms = None
    
    def send_sms(self, phone_number, message, notification_id=None):
        """
        Send SMS using Africa's Talking
        
        Args:
            phone_number (str): Recipient phone number
            message (str): SMS message content
            notification_id (str): Optional notification ID for tracking
            
        Returns:
            dict: Response with status and details
        """
        if not self.sms:
            logger.error("SMS service not initialized")
            return {
                'success': False,
                'error': 'SMS service not initialized'
            }
        
        try:
            logger.info(f"Sending SMS to {phone_number} - Message: {message[:50]}...")
            
            # Send SMS without sender_id (uses default Africa's Talking sender)
            if self.sender_id and self.sender_id != 'ORDERFLOW':
                logger.info(f"Using sender ID: {self.sender_id}")
                response = self.sms.send(message, [phone_number], sender_id=self.sender_id)
            else:
                logger.info("Using default Africa's Talking sender ID")
                response = self.sms.send(message, [phone_number])
            
            # Parse response
            sms_data = response['SMSMessageData']
            logger.info(f"Africa's Talking Response: {response}")
            
            # Check if there are recipients
            if 'Recipients' in sms_data and len(sms_data['Recipients']) > 0:
                recipient = sms_data['Recipients'][0]
                status = recipient.get('status', 'Unknown')
                
                if status == 'Success':
                    message_id = recipient.get('messageId', '')
                    cost = recipient.get('cost', '0')
                    
                    logger.info(f"SMS sent successfully to {phone_number} - Message ID: {message_id}, Cost: {cost}")
                    
                    # Update notification if ID provided
                    if notification_id:
                        self._update_notification(notification_id, message_id, cost, 'sent')
                    
                    return {
                        'success': True,
                        'message_id': message_id,
                        'cost': cost,
                        'status': 'sent'
                    }
                else:
                    error = f"{status}: {recipient.get('statusCode', '')}"
                    logger.error(f"SMS failed for {phone_number} - Status: {status}, Code: {recipient.get('statusCode', '')}")
                    
                    # Update notification if ID provided
                    if notification_id:
                        self._update_notification(notification_id, '', '0', 'failed', error)
                    
                    return {
                        'success': False,
                        'error': error
                    }
            else:
                # No recipients in response
                error = sms_data.get('Message', 'Unknown error')
                logger.error(f"SMS failed for {phone_number} - No recipients in response: {error}")
                
                # Update notification if ID provided
                if notification_id:
                    self._update_notification(notification_id, '', '0', 'failed', error)
                
                return {
                    'success': False,
                    'error': error
                }
                
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            
            # Update notification if ID provided
            if notification_id:
                self._update_notification(notification_id, '', '0', 'failed', str(e))
            
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_notification(self, notification_id, message_id, cost, status, error_message=''):
        """Update notification record with SMS details"""
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.status = status
            notification.sent_at = timezone.now()
            
            if error_message:
                notification.error_message = error_message
            
            notification.save()
            
            # Update SMS details
            sms_notification, created = SMSNotification.objects.get_or_create(
                notification=notification,
                defaults={
                    'phone_number': notification.recipient.phone_number,
                    'message_id': message_id,
                    'cost': cost
                }
            )
            
            if not created:
                sms_notification.message_id = message_id
                sms_notification.cost = cost
                sms_notification.save()
                
        except Exception as e:
            logger.error(f"Failed to update notification {notification_id}: {e}")
    
    def send_order_confirmation(self, order):
        """Send order confirmation SMS"""
        customer = order.customer
        message = f"""
Order #{order.order_number} confirmed!
Total: ${order.total_amount}
Status: {order.status.title()}
Thank you for your order!
        """.strip()
        
        # Create notification record
        notification = Notification.objects.create(
            notification_type='sms',
            recipient=customer,
            order=order,
            subject='Order Confirmation',
            message=message,
            status='pending'
        )
        
        # Send SMS
        result = self.send_sms(
            customer.phone_number,
            message,
            str(notification.id)
        )
        
        return result
    
    def send_order_status_update(self, order, old_status, new_status):
        """Send order status update SMS"""
        customer = order.customer
        message = f"""
Order #{order.order_number} status updated!
From: {old_status.title()}
To: {new_status.title()}
Track your order at our website.
        """.strip()
        
        # Create notification record
        notification = Notification.objects.create(
            notification_type='sms',
            recipient=customer,
            order=order,
            subject='Order Status Update',
            message=message,
            status='pending'
        )
        
        # Send SMS
        result = self.send_sms(
            customer.phone_number,
            message,
            str(notification.id)
        )
        
        return result
    
    def send_delivery_notification(self, order):
        """Send delivery notification SMS"""
        customer = order.customer
        message = f"""
Your order #{order.order_number} has been delivered!
Total: ${order.total_amount}
Thank you for shopping with us!
        """.strip()
        
        # Create notification record
        notification = Notification.objects.create(
            notification_type='sms',
            recipient=customer,
            order=order,
            subject='Order Delivered',
            message=message,
            status='pending'
        )
        
        # Send SMS
        result = self.send_sms(
            customer.phone_number,
            message,
            str(notification.id)
        )
        
        return result
