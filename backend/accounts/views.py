"""
User Profile and Brand Profile Views

File: views.py
Author: Anthony Bañon
Created: 2025-11-29
Last Updated: 2025-11-30
Changes: ApiViews for all views related to user profiles and brand profiles
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    BrandProfileSerializer,
    BrandManagerRegistrationSerializer,
    EcoPointsUpdateSerializer,
    BrandStoryUpdateSerializer,
    ChangePasswordSerializer,
)
from .services import auth_service, user_profile_service, brand_profile_service
from .constants import *
from .services import BusinessException


############# Authentication Views #############

class LoginUserView(APIView):
    """
    User login
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=UserLoginSerializer)
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = auth_service.login_user(
                    serializer.validated_data['username'],
                    serializer.validated_data['password']
                )
                return Response({
                    'message': SUCCESS_LOGIN,
                    'data': result
                })
                
            except BusinessException as e:
                return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutUserView(APIView):
    """
    User logout
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            auth_service.logout_user(request.user)
            return Response({'message': SUCCESS_LOGOUT})
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class ChangePasswordView(APIView):
    """
    Change user password
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                auth_service.change_password(
                    request.user.id,
                    serializer.validated_data['current_password'],
                    serializer.validated_data['new_password']
                )
                return Response({'message': SUCCESS_PASSWORD_CHANGED})
                
            except BusinessException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


############# User Profile Views #############

class RegisterUserView(APIView):
    """
    Register a new regular user
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=UserRegistrationSerializer)
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user_data = {
                    'username': serializer.validated_data['username'],
                    'email': serializer.validated_data['email'],
                    'password': serializer.validated_data['password'],
                    'first_name': serializer.validated_data.get('first_name', ''),
                    'last_name': serializer.validated_data.get('last_name', '')
                }
                
                profile_data = {
                    'phone': serializer.validated_data.get('phone', '')
                }
                
                result = user_profile_service.register_user(user_data, profile_data)
                return Response({
                    'message': SUCCESS_REGISTRATION,
                    'data': result
                }, status=status.HTTP_201_CREATED)
                
            except BusinessException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUserProfileView(APIView):
    """
    Get current user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            profile_data = user_profile_service.get_user_profile(request.user.id)
            serializer = UserProfileSerializer(profile_data)
            return Response(serializer.data)
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

class UpdateUserProfileView(APIView):
    """
    Update user profile information
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=UserProfileUpdateSerializer)
    def put(self, request):
        # 1. Validar datos con serializer
        serializer = UserProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Llamar al service con datos validados
        try:
            updated_profile = user_profile_service.update_user_profile(
                request.user.id, 
                serializer.validated_data
            )
            return Response({
                'message': SUCCESS_PROFILE_UPDATED,
                'data': updated_profile
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error interno del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AddEcoPointsView(APIView):
    """
    Add eco points and carbon saved to user profile
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=EcoPointsUpdateSerializer)
    def post(self, request):
        serializer = EcoPointsUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = user_profile_service.update_eco_points(
                    request.user.id, 
                    serializer.validated_data['points'],
                    serializer.validated_data.get('carbon_saved', MIN_CARBON_SAVED)
                )
                return Response({
                    'message': SUCCESS_ECO_POINTS_ADDED,
                    'data': result
                })
                
            except BusinessException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteUserAccountView(APIView):
    """
    Delete user account and all associated data
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        try:
            user_profile_service.delete_user(request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


############## Brand Profile Views #############

class RegisterBrandManagerView(APIView):
    """
    Register a new brand manager user
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=BrandManagerRegistrationSerializer)
    def post(self, request):
        serializer = BrandManagerRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user_data = {
                    'username': serializer.validated_data['username'],
                    'email': serializer.validated_data['email'],
                    'password': serializer.validated_data['password'],
                    'first_name': serializer.validated_data.get('first_name', ''),
                    'last_name': serializer.validated_data.get('last_name', '')
                }
                
                brand_data = {
                    'brand_name': serializer.validated_data['brand_name'],
                    'sustainability_story': serializer.validated_data.get('sustainability_story', '')
                }
                
                result = brand_profile_service.create_brand_manager(user_data, brand_data)
                return Response({
                    'message': SUCCESS_REGISTRATION,
                    'data': result
                }, status=status.HTTP_201_CREATED)
                
            except BusinessException as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GetBrandProfileView(APIView):
    """
    Get current user's brand profile (if brand manager)
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            brand_data = brand_profile_service.get_brand_profile(request.user.id)
            serializer = BrandProfileSerializer(brand_data)
            return Response(serializer.data)
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

class UpdateBrandStoryView(APIView):
    """
    Update brand sustainability story
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=BrandStoryUpdateSerializer)
    def put(self, request):
        serializer = BrandStoryUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                brand_profile = brand_profile_service.update_brand_story(
                    request.user.id, 
                    serializer.validated_data['sustainability_story']
                )
                return Response({
                    'message': SUCCESS_BRAND_STORY_UPDATED,
                    'data': BrandProfileSerializer(brand_profile).data
                })
                
            except BusinessException as e:
                return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteBrandProfileView(APIView):
    """
    Delete brand profile (user remains)
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        try:
            brand_profile_service.delete_brand_profile(request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


