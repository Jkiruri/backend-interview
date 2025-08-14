from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem"""
    model = OrderItem
    extra = 0
    readonly_fields = ['unit_price', 'subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model"""
    list_display = ['order_number', 'customer', 'status', 'total_amount', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer__email', 'customer__first_name', 'customer__last_name']
    ordering = ['-created_at']
    readonly_fields = ['order_number', 'total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'total_amount')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'shipping_address', 'billing_address')
        }),
        ('Payment', {
            'fields': ('is_paid', 'payment_method', 'payment_reference')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related('customer')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model"""
    list_display = ['order', 'product', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'product__name', 'product__sku']
    ordering = ['-created_at']
    readonly_fields = ['unit_price', 'subtotal', 'created_at']
    
    fieldsets = (
        (None, {
            'fields': ('order', 'product', 'quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price', 'subtotal')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related('order', 'product')
