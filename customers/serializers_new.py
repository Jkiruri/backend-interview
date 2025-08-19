from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import Customer, Admin


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for customer registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'email', 'first_name', 'last_name', 'phone_number',
            'address', 'city', 'state', 'country', 'postal_code', 
            'password', 'password_confirm'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create a new customer"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        customer = Customer.objects.create(**validated_data)
        customer.set_password(password)
        customer.save()
        return customer


class CustomerLoginSerializer(serializers.Serializer):
    """Serializer for customer login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')
        
        return attrs


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer profile"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'address', 'city', 'state', 'country', 
            'postal_code', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (e.g., +254).")
        return value


class CustomerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating customer profile"""
    
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'phone_number',
            'address', 'city', 'state', 'country', 'postal_code'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (e.g., +254).")
        return value


# Admin Serializers
class AdminSerializer(serializers.ModelSerializer):
    """Serializer for Admin model"""
    
    class Meta:
        model = Admin
        fields = [
            'id', 'user', 'role', 'permissions', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating admin users"""
    
    class Meta:
        model = Admin
        fields = [
            'user', 'role', 'permissions', 'is_active'
        ]


class AdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating admin users"""
    
    class Meta:
        model = Admin
        fields = [
            'role', 'permissions', 'is_active'
        ]


class CustomerAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin customer management"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'address', 'city', 'state', 'country', 
            'postal_code', 'is_verified', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']


class DashboardSerializer(serializers.Serializer):
    """Serializer for admin dashboard data"""
    orders = serializers.DictField()
    customers = serializers.DictField()
    products = serializers.DictField()
    notifications = serializers.DictField()


class SystemAlertSerializer(serializers.Serializer):
    """Serializer for system alerts"""
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    alert_type = serializers.CharField(max_length=50)


class AdminPermissionSerializer(serializers.Serializer):
    """Serializer for admin permissions"""
    permissions = serializers.ListField(child=serializers.CharField())
