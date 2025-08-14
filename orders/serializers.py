from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from customers.models import Customer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'quantity', 'unit_price', 'subtotal', 'created_at'
        ]
        read_only_fields = ['unit_price', 'subtotal', 'created_at']
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate_product(self, value):
        """Validate product is active and in stock"""
        if value.status != 'active':
            raise serializers.ValidationError("Product is not available for ordering.")
        return value


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating order items"""
    product_id = serializers.UUIDField(write_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'product_id', 'product_name', 'product_sku',
            'quantity', 'unit_price', 'subtotal'
        ]
        read_only_fields = ['unit_price', 'subtotal']
    
    def validate(self, attrs):
        """Validate order item data"""
        product_id = attrs.get('product_id')
        quantity = attrs.get('quantity', 0)
        
        try:
            product = Product.objects.get(id=product_id, status='active')
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available.")
        
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        
        if product.stock_quantity < quantity:
            raise serializers.ValidationError(f"Insufficient stock. Available: {product.stock_quantity}")
        
        attrs['product'] = product
        attrs['unit_price'] = product.price
        attrs['subtotal'] = product.price * quantity
        
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model"""
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    items_count = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'customer_email',
            'status', 'total_amount', 'shipping_address', 'billing_address',
            'phone_number', 'notes', 'is_paid', 'payment_method',
            'payment_reference', 'created_at', 'updated_at',
            'items', 'items_count', 'can_be_cancelled'
        ]
        read_only_fields = [
            'id', 'order_number', 'total_amount', 'created_at', 'updated_at'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (e.g., +254).")
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = OrderItemCreateSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'shipping_address', 'billing_address', 'phone_number',
            'notes', 'payment_method', 'items'
        ]
    
    def validate(self, attrs):
        """Validate order data"""
        items = attrs.get('items', [])
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")
        
        # Calculate total amount
        total_amount = sum(item['subtotal'] for item in items)
        attrs['total_amount'] = total_amount
        
        return attrs
    
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop('items')
        customer = self.context['request'].user
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            **validated_data
        )
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        # Calculate and save total
        order.calculate_total()
        order.save()
        
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status"""
    
    class Meta:
        model = Order
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        """Validate status transition"""
        current_status = self.instance.status if self.instance else None
        
        # Define allowed status transitions
        allowed_transitions = {
            'pending': ['confirmed', 'cancelled'],
            'confirmed': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': ['refunded'],
            'cancelled': [],
            'refunded': []
        }
        
        if current_status and value not in allowed_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}."
            )
        
        return value
