"""
Views - Use appropriate view type for each case

File: views.py
Author: Anthony Bañon
Created: 2025-12-01
"""

from rest_framework import generics, viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from rest_framework.authtoken.models import Token

from .models import UserProfile, BrandProfile
from .serializers import *
from .services import AuthService, BrandService, BusinessException
from .constants import *


##### Authentication Views (APIView for complex logic) #####

class LoginUserView(APIView):
    """✅ APIView for complex authentication logic"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = AuthService().login_user(
                serializer.validated_data['username'],
                serializer.validated_data['password']
            )
            
            return Response({
                'message': SUCCESS_LOGIN,
                'data': {
                    'user_id': result['user'].id,
                    'username': result['user'].username,
                    'email': result['user'].email,
                    'token': result['token'].key,
                    'is_brand_manager': result['profile'].is_brand_manager,
                    'eco_points': result['profile'].eco_points,
                    'total_carbon_saved': result['profile'].total_carbon_saved
                }
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutUserView(APIView):
    """✅ APIView simple but specific logic"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'message': SUCCESS_LOGOUT})


class ChangePasswordView(APIView):
    """✅ APIView for complex password logic"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            AuthService().change_password(
                request.user,
                serializer.validated_data['current_password'],
                serializer.validated_data['new_password']
            )
            return Response({'message': SUCCESS_PASSWORD_CHANGED})
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


##### User Views (Generic Views for simple CRUD) #####

class RegisterUserView(generics.CreateAPIView):
    """✅ CreateAPIView uses Service for complex registration"""
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        # Validate input
        serializer = self.get_serializer(data=request.data)
        # Raise exception if invalid
        serializer.is_valid(raise_exception=True)
        
        try:
            # Use service to handle complex registration logic
            result = AuthService().register_user(
                serializer.validated_data,
                {'phone': serializer.validated_data.get('phone', '')}
            )
            
            return Response({
                'message': SUCCESS_REGISTRATION,
                'data': {
                    'user_id': result['user'].id,
                    'username': result['user'].username,
                    'email': result['user'].email,
                    'first_name': result['user'].first_name,
                    'last_name': result['user'].last_name,
                    'token': result['token'].key,
                    'is_brand_manager': result['profile'].is_brand_manager
                }
            }, status=status.HTTP_201_CREATED)
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.GenericViewSet, 
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin):
    """✅ ViewSet for simple user profile CRUD"""
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'update':
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Simple update logic in view (no service needed)
        user = instance.user
        if 'first_name' in serializer.validated_data:
            user.first_name = serializer.validated_data['first_name']
        if 'last_name' in serializer.validated_data:
            user.last_name = serializer.validated_data['last_name']
        user.save()
        
        if 'phone' in serializer.validated_data:
            instance.phone = serializer.validated_data['phone']
        instance.save()
        
        return Response({
            'message': SUCCESS_PROFILE_UPDATED,
            'data': UserProfileSerializer(instance).data
        })
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def add_eco_points(self, request):
        """✅ Custom action in ViewSet (simple logic stays in view)"""
        serializer = EcoPointsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        points = serializer.validated_data['points']
        carbon_saved = serializer.validated_data.get('carbon_saved', MIN_CARBON_SAVED)
        
        if abs(points) > MAX_ECO_POINTS_ADDITION:
            return Response({'error': ERROR_POINTS_EXCEED_LIMIT}, status=status.HTTP_400_BAD_REQUEST)
        
        if abs(carbon_saved) > MAX_CARBON_SAVED_ADDITION:
            return Response({'error': ERROR_CARBON_EXCEED_LIMIT}, status=status.HTTP_400_BAD_REQUEST)
        
        user_profile = self.get_object()
        user_profile.eco_points += points
        user_profile.total_carbon_saved += carbon_saved
        
        user_profile.eco_points = max(MIN_ECO_POINTS, user_profile.eco_points)
        user_profile.total_carbon_saved = max(MIN_CARBON_SAVED, user_profile.total_carbon_saved)
        user_profile.save()
        
        return Response({
            'message': SUCCESS_ECO_POINTS_ADDED,
            'data': {
                'eco_points': user_profile.eco_points,
                'total_carbon_saved': user_profile.total_carbon_saved,
                'points_added': points,
                'carbon_saved_added': carbon_saved
            }
        })
    
    @action(detail=False, methods=['delete'])
    @transaction.atomic
    def delete_account(self, request):
        """✅ Custom action (simple delete logic in view)"""
        user = request.user
        
        Token.objects.filter(user=user).delete()
        
        try:
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.is_brand_manager:
                BrandProfile.objects.filter(user_profile=user_profile).delete()
            user_profile.delete()
        except UserProfile.DoesNotExist:
            pass
        
        user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


##### Brand Views #####

class RegisterBrandManagerView(generics.CreateAPIView):
    """✅ CreateAPIView uses Service for complex brand creation"""
    permission_classes = [AllowAny]
    serializer_class = BrandManagerRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = BrandService().create_brand_manager(
                serializer.validated_data,
                {
                    'brand_name': serializer.validated_data['brand_name'],
                    'sustainability_story': serializer.validated_data.get('sustainability_story', '')
                }
            )
            
            return Response({
                'message': SUCCESS_REGISTRATION,
                'data': {
                    'user_id': result['user'].id,
                    'username': result['user'].username,
                    'email': result['user'].email,
                    'first_name': result['user'].first_name,
                    'last_name': result['user'].last_name,
                    'token': result['token'].key,
                    'is_brand_manager': True,
                    'brand_id': result['brand_profile'].id,
                    'brand_name': result['brand_profile'].brand_name,
                    'sustainability_story': result['brand_profile'].sustainability_story
                }
            }, status=status.HTTP_201_CREATED)
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BrandProfileView(generics.RetrieveAPIView):
    """✅ RetrieveAPIView for simple GET (no service needed)"""
    permission_classes = [IsAuthenticated]
    serializer_class = BrandProfileSerializer
    
    def get_object(self):
        try:
            user_profile = UserProfile.objects.get(
                user=self.request.user, 
                is_brand_manager=True
            )
            return BrandProfile.objects.get(user_profile=user_profile)
        except (UserProfile.DoesNotExist, BrandProfile.DoesNotExist):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(ERROR_NOT_BRAND_MANAGER)


class UpdateBrandStoryView(APIView):
    """✅ APIView uses Service for complex update logic"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=BrandStoryUpdateSerializer)
    def put(self, request):
        serializer = BrandStoryUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            brand_profile = BrandService().update_brand_story(
                request.user,
                serializer.validated_data['sustainability_story']
            )
            
            return Response({
                'message': SUCCESS_BRAND_STORY_UPDATED,
                'data': BrandProfileSerializer(brand_profile).data
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class DeleteBrandProfileView(APIView):
    """✅ APIView uses Service for complex delete logic"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        try:
            BrandService().delete_brand_profile(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)