"""
URL configuration for orderflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.views.decorators.csrf import csrf_exempt

# Import views
from customers.views import (
    CustomerRegistrationView, CustomerLoginView, CustomerLogoutView, CustomerViewSet
)
from customers.admin_views import AdminViewSet, CustomerAdminViewSet
from customers.oidc_views import CustomerOIDCLoginView, oidc_token_login, oidc_user_info
from customers.google_oauth import google_login, google_token_login, google_user_info
from products.views import CategoryViewSet, ProductViewSet
from orders.views import OrderViewSet
from notifications.views import NotificationViewSet, NotificationAdminViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'admin/notifications', NotificationAdminViewSet, basename='admin-notification')

# Admin router
admin_router = DefaultRouter()
admin_router.register(r'admin', AdminViewSet, basename='admin')
admin_router.register(r'admin/customers', CustomerAdminViewSet, basename='admin-customer')

# Swagger/OpenAPI documentation
schema_view = get_schema_view(
    openapi.Info(
        title="OrderFlow API",
        default_version='v1',
        description="E-commerce Order Management System API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@orderflow.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # OIDC URLs
    path('oidc/', include('mozilla_django_oidc.urls')),
    
    # Allauth URLs
    path('accounts/', include('allauth.urls')),
    
    # API URLs
    path('api/v1/', include([
        # Authentication endpoints
        path('auth/register/', CustomerRegistrationView.as_view(), name='customer-register'),
        path('auth/login/', CustomerLoginView.as_view(), name='customer-login'),
        path('auth/logout/', CustomerLogoutView.as_view(), name='customer-logout'),
        path('auth/token/', obtain_auth_token, name='api-token-auth'),
        
        # OIDC Authentication endpoints
        path('auth/oidc/login/', CustomerOIDCLoginView.as_view(), name='oidc-login'),
        path('auth/oidc/token/', oidc_token_login, name='oidc-token-login'),
        path('auth/oidc/userinfo/', oidc_user_info, name='oidc-user-info'),
        
        # Google OAuth2 endpoints
        path('auth/google/login/', google_login, name='google-login'),
        path('auth/google/token/', google_token_login, name='google-token-login'),
        path('auth/google/userinfo/', google_user_info, name='google-user-info'),
        
        # Router URLs for ViewSets
        path('', include(router.urls)),
        path('', include(admin_router.urls)),
    ])),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api-docs/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
