from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    OrderItemSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Order model with order management"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_paid']
    search_fields = ['order_number', 'customer__email', 'customer__first_name']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return orders based on user permissions"""
        if self.request.user.is_staff:
            return Order.objects.select_related('customer').prefetch_related('items')
        return Order.objects.filter(customer=self.request.user).select_related('customer').prefetch_related('items')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update_status', 'partial_update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['update_status', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Create order with additional logic"""
        order = serializer.save()
        
        # Update stock quantities
        for item in order.items.all():
            product = item.product
            product.stock_quantity = max(0, product.stock_quantity - item.quantity)
            product.save()
        
        # TODO: Send SMS and email notifications
        # This will be implemented in Phase 3
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status with validation"""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        
        if serializer.is_valid():
            old_status = order.status
            serializer.save()
            
            # If status changed to confirmed, update stock
            if old_status != 'confirmed' and order.status == 'confirmed':
                order.update_stock()
            
            return Response(OrderSerializer(order).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        
        if not order.can_be_cancelled:
            return Response(
                {'error': 'Order cannot be cancelled in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        
        # Restore stock quantities
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()
        
        return Response(OrderSerializer(order).data)
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Get current user's orders"""
        orders = self.get_queryset().filter(customer=request.user)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending orders (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_orders = self.get_queryset().filter(status='pending')
        page = self.paginate_queryset(pending_orders)
        if page is not None:
            serializer = OrderSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = OrderSerializer(pending_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get order statistics (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Access denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = Order.objects.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount'),
            pending_orders=Count('id', filter={'status': 'pending'}),
            completed_orders=Count('id', filter={'status': 'delivered'})
        )
        
        return Response(stats)
