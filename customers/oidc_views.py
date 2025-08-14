from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.urls import reverse
from mozilla_django_oidc.views import OIDCAuthenticationRequestView
from .serializers import CustomerSerializer


class CustomerOIDCLoginView(OIDCAuthenticationRequestView):
    """Custom OIDC login view for customers"""
    
    def get(self, request, *args, **kwargs):
        """Initiate OIDC login flow"""
        # Store the intended redirect URL
        request.session['oidc_next'] = request.GET.get('next', '/api/v1/')
        return super().get(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([AllowAny])
def oidc_callback(request):
    """Handle OIDC callback and return API token"""
    # This will be handled by mozilla_django_oidc
    # We'll create a custom callback that returns API token
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def oidc_token_login(request):
    """Login with OIDC token and return API token"""
    # This endpoint would be used for mobile apps or SPAs
    # that handle OIDC flow and want to get a Django token
    
    id_token = request.data.get('id_token')
    access_token = request.data.get('access_token')
    
    if not id_token or not access_token:
        return Response(
            {'error': 'id_token and access_token are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify the token and get user
    # This is a simplified version - in production you'd verify the JWT
    try:
        # For now, we'll use a simple approach
        # In production, you'd verify the JWT signature
        user = authenticate(request, oidc_token=id_token)
        
        if user and user.is_active:
            # Create or get API token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'customer': CustomerSerializer(user).data,
                'message': 'OIDC login successful'
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        return Response(
            {'error': f'Authentication failed: {str(e)}'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
def oidc_user_info(request):
    """Get current user info from OIDC"""
    if request.user.is_authenticated:
        return Response({
            'user': CustomerSerializer(request.user).data,
            'oidc_info': {
                'access_token': getattr(request.user, 'oidc_access_token', None),
                'id_token': getattr(request.user, 'oidc_id_token', None),
            }
        })
    else:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
