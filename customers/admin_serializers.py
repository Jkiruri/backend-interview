from rest_framework import serializers
from .models import Admin, Customer


class AdminSerializer(serializers.ModelSerializer):
    """Serializer for Admin model"""
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    created_at = serializers.DateTimeField(source='user.created_at', read_only=True)
    
    class Meta:
        model = Admin
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'permissions', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminCreateSerializer(serializers.Serializer):
    """Serializer for creating admin users"""
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=[
        ('admin', 'Administrator'),
        ('super_admin', 'Super Administrator'),
        ('manager', 'Manager'),
    ], default='admin')
    permissions = serializers.JSONField(default=dict)


class AdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating admin users"""
    
    class Meta:
        model = Admin
        fields = ['role', 'permissions', 'is_active']


class CustomerAdminSerializer(serializers.ModelSerializer):
    """Serializer for customer management by admins"""
    full_name = serializers.CharField(read_only=True)
    is_admin = serializers.BooleanField(read_only=True)
    admin_role = serializers.CharField(source='get_admin_role', read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'address', 'city', 'state', 'country',
            'is_verified', 'is_active', 'email_verified', 'phone_verified',
            'created_at', 'updated_at', 'is_admin', 'admin_role'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardSerializer(serializers.Serializer):
    """Serializer for admin dashboard data"""
    orders = serializers.DictField()
    customers = serializers.DictField()
    products = serializers.DictField()
    notifications = serializers.DictField()


class SystemAlertSerializer(serializers.Serializer):
    """Serializer for system alerts"""
    alert_type = serializers.ChoiceField(choices=[
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
    ], default='info')
    message = serializers.CharField()
    details = serializers.JSONField(required=False)


class AdminPermissionSerializer(serializers.Serializer):
    """Serializer for admin permissions"""
    permissions = serializers.JSONField()
