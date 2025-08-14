from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    """Admin interface for Customer model"""
    list_display = ['email', 'first_name', 'last_name', 'phone_number', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'date_of_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
