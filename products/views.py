from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Min, Max, Count
from django.shortcuts import get_object_or_404
from .models import Category, Product
from .serializers import (
    CategorySerializer, CategoryTreeSerializer, ProductSerializer,
    ProductUploadSerializer, CategoryAveragePriceSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Category model with hierarchical support"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Return active categories by default"""
        queryset = Category.objects.all()
        if self.action == 'list':
            queryset = queryset.filter(is_active=True)
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'tree':
            return CategoryTreeSerializer
        return CategorySerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get hierarchical category tree"""
        root_categories = Category.objects.filter(parent=None, is_active=True)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def average_price(self, request):
        """Get average price for a specific category by slug"""
        slug = request.query_params.get('slug')
        if not slug:
            return Response(
                {'error': 'slug parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get products in this category and its descendants
        descendant_ids = [category.id] + [c.id for c in category.get_descendants()]
        products = Product.objects.filter(
            category_id__in=descendant_ids,
            status='active'
        )
        
        if not products.exists():
            return Response({
                'category_id': category.id,
                'category_name': category.name,
                'category_slug': category.slug,
                'average_price': 0,
                'product_count': 0,
                'min_price': 0,
                'max_price': 0
            })
        
        # Calculate statistics
        stats = products.aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            product_count=Count('id')
        )
        
        data = {
            'category_id': category.id,
            'category_name': category.name,
            'category_slug': category.slug,
            'average_price': stats['avg_price'] or 0,
            'product_count': stats['product_count'],
            'min_price': stats['min_price'] or 0,
            'max_price': stats['max_price'] or 0
        }
        
        serializer = CategoryAveragePriceSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def average_price_per_category(self, request):
        """Get average price for all categories"""
        from django.db.models import Avg, Count
        
        # Get all categories with products
        categories = Category.objects.filter(
            products__isnull=False
        ).distinct()
        
        result = []
        for category in categories:
            # Get products in this category and its descendants
            descendant_ids = [category.id] + [c.id for c in category.get_descendants()]
            products = Product.objects.filter(
                category_id__in=descendant_ids,
                status='active'
            )
            
            if products.exists():
                avg_price = products.aggregate(avg_price=Avg('price'))['avg_price'] or 0
                product_count = products.count()
                
                result.append({
                    'category_id': category.id,
                    'category_name': category.name,
                    'category_slug': category.slug,
                    'average_price': float(avg_price),
                    'product_count': product_count
                })
        
        return Response(result)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for Product model with upload support"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_featured']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return active products by default"""
        queryset = Product.objects.select_related('category')
        if self.action == 'list':
            queryset = queryset.filter(status='active')
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'upload':
            return ProductUploadSerializer
        return ProductSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'upload']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload product with image"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            response_serializer = ProductSerializer(product)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_featured(self, request, pk=None):
        """Toggle product featured status"""
        product = self.get_object()
        product.is_featured = not product.is_featured
        product.save()
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(featured_products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(featured_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with low stock (less than 10 items)"""
        low_stock_products = self.get_queryset().filter(stock_quantity__lt=10)
        page = self.paginate_queryset(low_stock_products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(low_stock_products, many=True)
        return Response(serializer.data)
