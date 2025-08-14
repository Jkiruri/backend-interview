from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class APITokenAuthentication(TokenAuthentication):
    """Custom token authentication that doesn't require CSRF"""
    
    def authenticate(self, request):
        """Authenticate the request and return a two-tuple of (user, token)."""
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth:
            return None
            
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            return None
