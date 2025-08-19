from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta

from .models import Customer, Admin
from .serializers import CustomerSerializer, AdminSerializer
from products.models import Product, Category
from orders.models import Order, OrderItem
from notifications.models import Notification
from notifications.admin_service import AdminService

User = get_user_model()


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()


class AdminViewSet(viewsets.ViewSet):
    """Admin viewset for system management"""
    permission_classes = [IsAdminUser]
    admin_service = AdminService()
    
    def get_queryset(self):
        """Return appropriate queryset based on action"""
        return Admin.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        return AdminSerializer
    
    def list(self, request):
        """List all admin users"""
        queryset = self.get_queryset()
        serializer = AdminSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_object(self):
        """Get admin object by ID"""
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = queryset.get(**filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get admin dashboard statistics"""
        try:
            # Get date range (last 30 days)
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            # Orders statistics
            total_orders = Order.objects.count()
            recent_orders = Order.objects.filter(created_at__gte=start_date).count()
            pending_orders = Order.objects.filter(status='pending').count()
            completed_orders = Order.objects.filter(status='completed').count()
            total_revenue = Order.objects.filter(status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            # Customers statistics
            total_customers = Customer.objects.count()
            new_customers = Customer.objects.filter(created_at__gte=start_date).count()
            
            # Products statistics
            total_products = Product.objects.count()
            low_stock_products = Product.objects.filter(stock_quantity__lte=10).count()
            
            # Notifications statistics
            total_notifications = Notification.objects.count()
            recent_notifications = Notification.objects.filter(created_at__gte=start_date).count()
            failed_notifications = Notification.objects.filter(status='failed').count()
            
            # Recent orders
            recent_order_list = Order.objects.filter(
                created_at__gte=start_date
            ).order_by('-created_at')[:10]
            
            # Low stock products
            low_stock_list = Product.objects.filter(
                stock_quantity__lte=10
            ).order_by('stock_quantity')[:10]
            
            dashboard_data = {
                'orders': {
                    'total': total_orders,
                    'recent': recent_orders,
                    'pending': pending_orders,
                    'completed': completed_orders,
                    'revenue': float(total_revenue),
                    'recent_list': [
                        {
                            'id': str(order.id),
                            'order_number': order.order_number,
                            'customer': order.customer.full_name,
                            'amount': float(order.total_amount),
                            'status': order.status,
                            'created_at': order.created_at.isoformat()
                        }
                        for order in recent_order_list
                    ]
                },
                'customers': {
                    'total': total_customers,
                    'new': new_customers
                },
                'products': {
                    'total': total_products,
                    'low_stock': low_stock_products,
                    'low_stock_list': [
                        {
                            'id': str(product.id),
                            'name': product.name,
                            'stock_quantity': product.stock_quantity,
                            'category': product.category.name
                        }
                        for product in low_stock_list
                    ]
                },
                'notifications': {
                    'total': total_notifications,
                    'recent': recent_notifications,
                    'failed': failed_notifications
                }
            }
            
            return Response(dashboard_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def create_admin(self, request):
        """Create a new admin user"""
        try:
            email = request.data.get('email')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            password = request.data.get('password')
            role = request.data.get('role', 'admin')
            permissions = request.data.get('permissions', {})
            
            if not all([email, first_name, last_name, password]):
                return Response(
                    {'error': 'Email, first_name, last_name, and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            admin = self.admin_service.create_admin_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=role,
                permissions=permissions
            )
            
            return Response({
                'success': True,
                'admin': AdminSerializer(admin).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_permissions(self, request, pk=None):
        """Update admin permissions"""
        try:
            admin = self.get_object()
            permissions = request.data.get('permissions', {})
            
            updated_admin = self.admin_service.update_admin_permissions(
                admin.id, permissions
            )
            
            return Response({
                'success': True,
                'admin': AdminSerializer(updated_admin).data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate an admin user"""
        try:
            admin = self.get_object()
            
            deactivated_admin = self.admin_service.deactivate_admin(admin.id)
            
            return Response({
                'success': True,
                'message': f'Admin {deactivated_admin.email} has been deactivated'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def send_system_alert(self, request):
        """Send system alert to all admins"""
        try:
            alert_type = request.data.get('alert_type', 'info')
            message = request.data.get('message')
            details = request.data.get('details')
            
            if not message:
                return Response(
                    {'error': 'Message is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.admin_service.send_system_alert_to_admins(
                alert_type, message, details
            )
            
            return Response({
                'success': result['success'],
                'total_admins': result['total_admins'],
                'success_count': result['success_count']
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def send_daily_report(self, request):
        """Send daily report to all admins"""
        try:
            # Generate report data
            end_date = timezone.now()
            start_date = end_date - timedelta(days=1)
            
            report_data = {
                'total_orders': Order.objects.count(),
                'new_orders': Order.objects.filter(created_at__gte=start_date).count(),
                'completed_orders': Order.objects.filter(status='completed').count(),
                'pending_orders': Order.objects.filter(status='pending').count(),
                'total_revenue': float(Order.objects.filter(status='completed').aggregate(
                    total=Sum('total_amount')
                )['total'] or 0),
                'total_customers': Customer.objects.count(),
                'new_customers': Customer.objects.filter(created_at__gte=start_date).count(),
                'total_products': Product.objects.count(),
                'low_stock_items': Product.objects.filter(stock_quantity__lte=10).count(),
                'notifications_sent': Notification.objects.filter(status='sent').count(),
                'failed_notifications': Notification.objects.filter(status='failed').count(),
                'system_uptime': '99.9%'  # This would be calculated from monitoring
            }
            
            result = self.admin_service.send_daily_report_to_admins(report_data)
            
            return Response({
                'success': result['success'],
                'total_admins': result['total_admins'],
                'success_count': result['success_count'],
                'report_data': report_data
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomerAdminViewSet(viewsets.ModelViewSet):
    """Admin viewset for customer management"""
    permission_classes = [IsAdminUser]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a customer account"""
        try:
            customer = self.get_object()
            customer.is_verified = True
            customer.save()
            
            return Response({
                'success': True,
                'message': f'Customer {customer.email} has been verified'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a customer account"""
        try:
            customer = self.get_object()
            customer.is_active = False
            customer.save()
            
            return Response({
                'success': True,
                'message': f'Customer {customer.email} has been deactivated'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
