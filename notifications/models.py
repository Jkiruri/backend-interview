from django.db import models
from django.contrib.auth import get_user_model
from orders.models import Order
import uuid

Customer = get_user_model()

class Notification(models.Model):
    """Base notification model"""
    NOTIFICATION_TYPES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
    ]
    
    NOTIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    recipient = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=NOTIFICATION_STATUS, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type.upper()} to {self.recipient.email} - {self.status}"
    
    @property
    def can_retry(self):
        """Check if notification can be retried"""
        return self.status == 'failed' and self.retry_count < self.max_retries


class SMSNotification(models.Model):
    """SMS-specific notification details"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='sms_details')
    phone_number = models.CharField(max_length=17)
    message_id = models.CharField(max_length=100, blank=True)  # Africa's Talking message ID
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    units = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'sms_notifications'
        verbose_name = 'SMS Notification'
        verbose_name_plural = 'SMS Notifications'
    
    def __str__(self):
        return f"SMS to {self.phone_number} - {self.notification.status}"


class EmailNotification(models.Model):
    """Email-specific notification details"""
    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, related_name='email_details')
    email_address = models.EmailField()
    message_id = models.CharField(max_length=100, blank=True)  # Email provider message ID
    template_used = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'email_notifications'
        verbose_name = 'Email Notification'
        verbose_name_plural = 'Email Notifications'
    
    def __str__(self):
        return f"Email to {self.email_address} - {self.notification.status}"
