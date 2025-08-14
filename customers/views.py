from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from .models import Customer
from .serializers import (
    CustomerRegistrationSerializer, CustomerLoginSerializer,
    CustomerSerializer, CustomerProfileUpdateSerializer
)


class CustomerRegistrationView(generics.CreateAPIView):
    """View for customer registration"""
    queryset = Customer.objects.all()
    serializer_class = CustomerRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create a new customer account"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            # Create authentication token
            token, created = Token.objects.get_or_create(user=customer)
            
            response_data = {
                'message': 'Customer registered successfully',
                'customer': CustomerSerializer(customer).data,
                'token': token.key
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginView(generics.GenericAPIView):
    """View for customer login"""
    serializer_class = CustomerLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Authenticate customer and return token"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            # Create or get authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            response_data = {
                'message': 'Login successful',
                'customer': CustomerSerializer(user).data,
                'token': token.key
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLogoutView(generics.GenericAPIView):
    """View for customer logout"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Logout customer and delete token"""
        try:
            # Delete the user's token
            request.user.auth_token.delete()
        except:
            pass
        
        logout(request)
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer model"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's profile"""
        return Customer.objects.filter(id=self.request.user.id)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['update', 'partial_update']:
            return CustomerProfileUpdateSerializer
        return CustomerSerializer
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = CustomerProfileUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(CustomerSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password"""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Invalid old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Password changed successfully'})
