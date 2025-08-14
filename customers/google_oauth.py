from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import redirect
from django.urls import reverse
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView, OAuth2CallbackView
from allauth.socialaccount.models import SocialAccount
from .serializers import CustomerSerializer


class GoogleOAuth2LoginView(OAuth2LoginView):
    """Google OAuth2 login view"""
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


class GoogleOAuth2CallbackView(OAuth2CallbackView):
    """Google OAuth2 callback view"""
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


@api_view(['GET'])
@permission_classes([AllowAny])
def google_login(request):
    """Initiate Google OAuth2 login"""
    # Redirect to Google OAuth2
    return redirect('socialaccount_signin', provider='google')


@api_view(['POST'])
@permission_classes([AllowAny])
def google_token_login(request):
    """Login with Google OAuth2 token and return API token"""
    access_token = request.data.get('access_token')
    
    if not access_token:
        return Response(
            {'error': 'access_token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Verify the token with Google
        from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
        adapter = GoogleOAuth2Adapter()
        
        # Get user info from Google
        user_info = adapter.get_provider().sociallogin_from_response(request, {
            'access_token': access_token
        })
        
        if user_info and user_info.is_existing:
            user = user_info.user
            
            # Create or get API token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'customer': CustomerSerializer(user).data,
                'message': 'Google OAuth2 login successful'
            })
        else:
            return Response(
                {'error': 'Invalid Google token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        return Response(
            {'error': f'Authentication failed: {str(e)}'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
def google_user_info(request):
    """Get current user's Google OAuth2 info"""
    if request.user.is_authenticated:
        try:
            social_account = SocialAccount.objects.get(
                user=request.user, 
                provider='google'
            )
            
            return Response({
                'user': CustomerSerializer(request.user).data,
                'google_info': {
                    'uid': social_account.uid,
                    'provider': social_account.provider,
                    'extra_data': social_account.extra_data,
                }
            })
        except SocialAccount.DoesNotExist:
            return Response({
                'user': CustomerSerializer(request.user).data,
                'google_info': None
            })
    else:
        return Response(
            {'error': 'Not authenticated'},
            status=status.HTTP_401_UNAUTHORIZED
        )
