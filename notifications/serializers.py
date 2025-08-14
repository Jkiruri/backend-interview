from rest_framework import serializers
from .models import Notification, SMSNotification, EmailNotification


class SMSNotificationSerializer(serializers.ModelSerializer):
    """Serializer for SMS notification details"""
    
    class Meta:
        model = SMSNotification
        fields = ['phone_number', 'message_id', 'cost', 'units']


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Serializer for email notification details"""
    
    class Meta:
        model = EmailNotification
        fields = ['email_address', 'message_id', 'template_used']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notification model"""
    sms_details = SMSNotificationSerializer(read_only=True)
    email_details = EmailNotificationSerializer(read_only=True)
    recipient_name = serializers.CharField(source='recipient.full_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'recipient', 'recipient_name',
            'order', 'order_number', 'subject', 'message', 'status',
            'sent_at', 'delivered_at', 'error_message', 'retry_count',
            'created_at', 'updated_at', 'sms_details', 'email_details'
        ]
        read_only_fields = [
            'id', 'sent_at', 'delivered_at', 'error_message', 
            'retry_count', 'created_at', 'updated_at'
        ]


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total = serializers.IntegerField()
    sms = serializers.IntegerField()
    email = serializers.IntegerField()
    pending = serializers.IntegerField()
    sent = serializers.IntegerField()
    failed = serializers.IntegerField()
    delivered = serializers.IntegerField()


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for sending custom notifications"""
    message = serializers.CharField(max_length=1000)
    subject = serializers.CharField(max_length=255, required=False, allow_blank=True)
    send_sms = serializers.BooleanField(default=True)
    send_email = serializers.BooleanField(default=True)
    customer_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )

