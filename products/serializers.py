from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model with hierarchical support"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    full_path = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'parent_name',
            'image', 'is_active', 'created_at', 'updated_at',
            'children_count', 'level', 'full_path'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        """Return the number of direct children"""
        return obj.children.count()
    
    def validate_parent(self, value):
        """Validate that parent is not the same as the category itself"""
        if self.instance and value and self.instance.id == value.id:
            raise serializers.ValidationError("A category cannot be its own parent.")
        return value


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer for displaying category hierarchy"""
    children = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'children', 'level', 'is_active']
    
    def get_children(self, obj):
        """Recursively get children categories"""
        children = obj.children.filter(is_active=True)
        return CategoryTreeSerializer(children, many=True, context=self.context).data


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_path = serializers.CharField(source='category.full_path', read_only=True)
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'category', 'category_name',
            'category_path', 'sku', 'stock_quantity', 'image', 'status',
            'is_featured', 'created_at', 'updated_at', 'is_in_stock'
        ]
        read_only_fields = ['slug', 'sku', 'created_at', 'updated_at']
    
    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
    
    def validate_stock_quantity(self, value):
        """Validate that stock quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value


class ProductUploadSerializer(serializers.ModelSerializer):
    """Serializer for product upload with file handling"""
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'category', 'stock_quantity',
            'image', 'status', 'is_featured'
        ]
    
    def validate(self, data):
        """Custom validation for product upload"""
        if data.get('price', 0) <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        
        if data.get('stock_quantity', 0) < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        
        return data


class CategoryAveragePriceSerializer(serializers.Serializer):
    """Serializer for category average price calculation"""
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_count = serializers.IntegerField()
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2)
