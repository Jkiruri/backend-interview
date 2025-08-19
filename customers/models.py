import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from model_utils import Choices


class CustomerManager(BaseUserManager):
    """Custom manager for Customer model"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Admin(models.Model):
    """Admin model for system administrators"""
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField('Customer', on_delete=models.CASCADE, related_name='admin_profile')
    role = models.CharField(max_length=50, default='admin', choices=[
        ('admin', 'Administrator'),
        ('super_admin', 'Super Administrator'),
        ('manager', 'Manager'),
    ])
    permissions = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Admin')
        verbose_name_plural = _('Admins')

    def __str__(self):
        return f"Admin: {self.user.full_name}"

    @property
    def email(self):
        return self.user.email

    @property
    def full_name(self):
        return self.user.full_name

    def has_permission(self, permission):
        """Check if admin has specific permission"""
        return permission in self.permissions.get('permissions', [])


class Customer(AbstractUser):
    """Customer model extending Django's AbstractUser"""
    id = models.AutoField(primary_key=True)
    
    # Remove username field and use email as primary identifier
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Personal Information
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # Address Information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Kenya')
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Account Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # OIDC fields
    oidc_id = models.CharField(max_length=255, blank=True, null=True)
    oidc_provider = models.CharField(max_length=100, blank=True, null=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomerManager()

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.first_name

    def is_admin(self):
        """Check if customer is an admin"""
        return hasattr(self, 'admin_profile')

    def get_admin_role(self):
        """Get admin role if customer is admin"""
        if self.is_admin():
            return self.admin_profile.role
        return None


class CustomerProfile(models.Model):
    """Extended customer profile information"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='profile')
    
    # Additional Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ], blank=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='Africa/Nairobi')
    
    # Marketing
    marketing_emails = models.BooleanField(default=False)
    marketing_sms = models.BooleanField(default=False)
    
    # Social Media
    facebook_id = models.CharField(max_length=100, blank=True)
    google_id = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Customer Profile')
        verbose_name_plural = _('Customer Profiles')

    def __str__(self):
        return f"Profile for {self.customer.email}"
