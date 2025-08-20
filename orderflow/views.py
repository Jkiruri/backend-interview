from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


def landing_page(request):
    """
    Landing page for the OrderFlow API
    """
    return render(request, 'landing.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """
    API information endpoint
    """
    api_info = {
        "name": "OrderFlow API",
        "version": "v1.0.0",
        "description": "E-commerce Order Management System API",
        "author": "Backend Engineer Assessment",
        "endpoints": {
            "authentication": {
                "register": "/api/v1/auth/register/",
                "login": "/api/v1/auth/login/",
                "logout": "/api/v1/auth/logout/",
                "token": "/api/v1/auth/token/",
                "oidc_login": "/api/v1/auth/oidc/login/",
                "google_login": "/api/v1/auth/google/login/"
            },
            "customers": "/api/v1/customers/",
            "categories": "/api/v1/categories/",
            "products": "/api/v1/products/",
            "orders": "/api/v1/orders/",
            "notifications": "/api/v1/notifications/",
            "admin": {
                "notifications": "/api/v1/admin/notifications/",
                "customers": "/api/v1/admin/customers/"
            }
        },
        "documentation": {
            "swagger": "/swagger/",
            "redoc": "/redoc/",
            "api_docs": "/api-docs/"
        },
        "features": [
            "RESTful API with Django REST Framework",
            "OpenID Connect Authentication",
            "Google OAuth2 Integration",
            "SMS Notifications via Africa's Talking",
            "Email Notifications",
            "Celery Task Queue",
            "PostgreSQL Database",
            "Docker Containerization",
            "Comprehensive API Documentation"
        ],
        "status": "active",
        "environment": "production"
    }
    
    return Response(api_info, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint
    """
    return Response({
        "status": "healthy",
        "service": "OrderFlow API",
        "timestamp": "2025-08-20T08:00:00Z"
    }, status=status.HTTP_200_OK)
