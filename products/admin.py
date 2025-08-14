from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""
    list_display = ['name', 'parent', 'level', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model"""
    list_display = ['name', 'sku', 'category', 'price', 'stock_quantity', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'is_featured', 'category', 'created_at']
    search_fields = ['name', 'sku', 'description']
    ordering = ['-created_at']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock_quantity', 'sku')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
    )
    
    readonly_fields = ['sku', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        """Auto-generate SKU if not provided"""
        if not obj.sku:
            obj.sku = f"SKU-{str(obj.id)[:8].upper()}"
        super().save_model(request, obj, form, change)
