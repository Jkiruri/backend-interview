from django.db import models
from django.core.validators import MinValueValidator
from customers.models import Customer
from products.models import Product
import uuid


class Order(models.Model):
    """
    Order model representing customer orders
    Contains order details and status tracking
    """
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='pending'
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    shipping_address = models.TextField()
    billing_address = models.TextField()
    phone_number = models.CharField(max_length=17)
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number: ORD-YYYYMMDD-XXXX
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(
                order_number__startswith=f'ORD-{date_str}'
            ).order_by('-order_number').first()
            
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.order_number = f"ORD-{date_str}-{new_number:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def items_count(self):
        """Returns the total number of items in the order"""
        return self.items.count()
    
    @property
    def can_be_cancelled(self):
        """Returns True if the order can be cancelled"""
        return self.status in ['pending', 'confirmed']
    
    def calculate_total(self):
        """Calculates the total amount based on order items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        return total
    
    def update_stock(self):
        """Updates product stock quantities when order is confirmed"""
        if self.status == 'confirmed':
            for item in self.items.all():
                product = item.product
                product.stock_quantity = max(0, product.stock_quantity - item.quantity)
                product.save()


class OrderItem(models.Model):
    """
    OrderItem model representing individual items within an order
    Links products to orders with quantity and price information
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name} - {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.price
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    @property
    def product_name(self):
        """Returns the product name"""
        return self.product.name
    
    @property
    def product_sku(self):
        """Returns the product SKU"""
        return self.product.sku
