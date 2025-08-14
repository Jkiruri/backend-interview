from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model
from django.db import transaction

Customer = get_user_model()


class CustomerOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """Custom OIDC authentication backend for Customer model"""
    
    def create_user(self, claims):
        """Create a new customer from OIDC claims"""
        email = claims.get('email')
        if not email:
            return None
        
        # Check if user already exists
        try:
            customer = Customer.objects.get(email=email)
            return customer
        except Customer.DoesNotExist:
            pass
        
        # Create new customer
        with transaction.atomic():
            customer = Customer.objects.create(
                email=email,
                first_name=claims.get('given_name', ''),
                last_name=claims.get('family_name', ''),
                is_verified=True,  # OIDC users are verified
                is_active=True
            )
            
            # Set a random password (not used for OIDC auth)
            customer.set_unusable_password()
            customer.save()
            
            return customer
    
    def update_user(self, user, claims):
        """Update existing customer with OIDC claims"""
        user.first_name = claims.get('given_name', user.first_name)
        user.last_name = claims.get('family_name', user.last_name)
        user.is_verified = True
        user.save()
        return user
    
    def filter_users_by_claims(self, claims):
        """Filter users by OIDC claims"""
        email = claims.get('email')
        if not email:
            return Customer.objects.none()
        
        return Customer.objects.filter(email=email)
    
    def verify_claims(self, claims):
        """Verify OIDC claims"""
        return 'email' in claims
