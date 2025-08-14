from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Notification
from .serializers import (
    NotificationSerializer, NotificationStatsSerializer, SendNotificationSerializer
)
from .notification_manager import NotificationManager

Customer = get_user_model()

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Notification model - read-only for customers"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'status', 'order']
    search_fields = ['subject', 'message']
    ordering_fields = ['created_at', 'sent_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return notifications for the current user"""
        if self.request.user.is_staff:
            return Notification.objects.all()
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics"""
        notification_manager = NotificationManager()
        
        if request.user.is_staff:
            stats = notification_manager.get_notification_stats()
        else:
            stats = notification_manager.get_notification_stats(request.user)
        
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed notification (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only administrators can retry notifications'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification = self.get_object()
        
        if not notification.can_retry:
            return Response(
                {'error': 'Notification cannot be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notification_manager = NotificationManager()
        
        if notification.notification_type == 'sms':
            result = notification_manager.sms_service.send_sms(
                notification.recipient.phone_number,
                notification.message,
                str(notification.id)
            )
        else:  # email
            result = notification_manager.email_service.send_email(
                notification.recipient.email,
                notification.subject,
                notification.message,
                str(notification.id)
            )
        
        if result['success']:
            notification.retry_count += 1
            notification.save()
            return Response({'message': 'Notification retried successfully'})
        else:
            return Response(
                {'error': result.get('error', 'Retry failed')},
                status=status.HTTP_400_BAD_REQUEST
            )


class NotificationAdminViewSet(viewsets.ModelViewSet):
    """Admin ViewSet for managing notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'status', 'recipient', 'order']
    search_fields = ['subject', 'message', 'recipient__email']
    ordering_fields = ['created_at', 'sent_at', 'status']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def send_custom(self, request):
        """Send custom notification to customers"""
        serializer = SendNotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification_manager = NotificationManager()
            results = []
            
            # Get customers to notify
            if serializer.validated_data.get('customer_ids'):
                customers = Customer.objects.filter(
                    id__in=serializer.validated_data['customer_ids']
                )
            else:
                # Send to all customers if no specific IDs provided
                customers = Customer.objects.all()
            
            # Send notifications
            for customer in customers:
                result = notification_manager.send_custom_notification(
                    customer=customer,
                    message=serializer.validated_data['message'],
                    subject=serializer.validated_data.get('subject', ''),
                    send_sms=serializer.validated_data.get('send_sms', True),
                    send_email=serializer.validated_data.get('send_email', True)
                )
                
                results.append({
                    'customer_id': str(customer.id),
                    'customer_email': customer.email,
                    'success': result['success'],
                    'sms_result': result.get('sms'),
                    'email_result': result.get('email'),
                    'error': result.get('error')
                })
            
            return Response({
                'message': f'Notifications sent to {len(customers)} customers',
                'results': results
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def send_test_sms(self, request):
        """Send test SMS to verify Africa's Talking integration"""
        phone_number = request.data.get('phone_number')
        message = request.data.get('message', 'Test SMS from OrderFlow')
        
        if not phone_number:
            return Response(
                {'error': 'phone_number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notification_manager = NotificationManager()
        result = notification_manager.sms_service.send_sms(phone_number, message)
        
        if result['success']:
            return Response({
                'message': 'Test SMS sent successfully',
                'message_id': result.get('message_id'),
                'cost': result.get('cost')
            })
        else:
            return Response(
                {'error': result.get('error', 'Failed to send SMS')},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def send_test_email(self, request):
        """Send test email to verify email configuration"""
        email = request.data.get('email')
        subject = request.data.get('subject', 'Test Email from OrderFlow')
        message = request.data.get('message', 'This is a test email from OrderFlow notification system.')
        
        if not email:
            return Response(
                {'error': 'email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notification_manager = NotificationManager()
        result = notification_manager.email_service.send_email(email, subject, message)
        
        if result['success']:
            return Response({
                'message': 'Test email sent successfully'
            })
        else:
            return Response(
                {'error': result.get('error', 'Failed to send email')},
                status=status.HTTP_400_BAD_REQUEST
            )
