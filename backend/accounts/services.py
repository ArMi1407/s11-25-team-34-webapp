"""
Service layer ONLY for complex business logic

File: services.py  
Author: Anthony Bañon
Created: 2025-12-01
"""

from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UserProfile, BrandProfile
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .constants import *


class BusinessException(Exception):
    """Custom exception for business logic errors"""
    pass


class AuthService:
    """
    Service ONLY for complex authentication logic
    """
    
    @transaction.atomic
    def register_user(self, user_data, profile_data=None):
        """
        Complex operation: Creates User + UserProfile + Token
        ASSUMES data already validated by serializer
        """
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        # Create user profile
        profile_data = profile_data or {}
        profile = UserProfile.objects.create(
            user=user,
            phone=profile_data.get('phone', ''),
            eco_points=DEFAULT_ECO_POINTS,
            total_carbon_saved=DEFAULT_CARBON_SAVED,
            is_brand_manager=profile_data.get('is_brand_manager', False)
        )
        
        # Create auth token
        token, _ = Token.objects.get_or_create(user=user)
        
        return {
            'user': user,
            'profile': profile,
            'token': token
        }
    
    def login_user(self, username, password):
        """
        Complex operation: Authenticate + get token + check business rules
        """
        user = authenticate(username=username, password=password)
        
        if not user:
            raise BusinessException(ERROR_INVALID_CREDENTIALS)
        
        if not user.is_active:
            raise BusinessException(ERROR_ACCOUNT_DEACTIVATED)
        
        token, _ = Token.objects.get_or_create(user=user)
        user_profile = UserProfile.objects.get(user=user)
        
        return {
            'user': user,
            'profile': user_profile,
            'token': token
        }
    
    @transaction.atomic
    def change_password(self, user, current_password, new_password):
        """
        Complex operation: Validate + change password + delete tokens
        """
        if not user.check_password(current_password):
            raise BusinessException(ERROR_INVALID_CREDENTIALS)
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            raise BusinessException(str(e))
        
        user.set_password(new_password)
        user.save()
        Token.objects.filter(user=user).delete()
        
        return True


class BrandService:
    """
    Service ONLY for complex brand operations
    """
    
    @transaction.atomic
    def create_brand_manager(self, user_data, brand_data):
        """
        Complex operation: User + BrandProfile + special business rules
        """
        # Check brand name uniqueness
        if BrandProfile.objects.filter(brand_name__iexact=brand_data['brand_name']).exists():
            raise BusinessException(ERROR_BRAND_NAME_EXISTS)
        
        # Create user with brand manager flag
        auth_service = AuthService()
        result = auth_service.register_user(
            user_data, 
            {'is_brand_manager': True}
        )
        
        # Create brand profile
        brand_profile = BrandProfile.objects.create(
            user_profile=result['profile'],
            brand_name=brand_data['brand_name'],
            sustainability_story=brand_data.get('sustainability_story', '')
        )
        
        return {
            'user': result['user'],
            'profile': result['profile'],
            'token': result['token'],
            'brand_profile': brand_profile
        }
    
    @transaction.atomic
    def update_brand_story(self, user, sustainability_story):
        """
        Complex operation: Update with business rules
        """
        if len(sustainability_story) > MAX_SUSTAINABILITY_STORY_LENGTH:
            raise BusinessException(ERROR_STORY_EXCEED_LENGTH)
        
        user_profile = UserProfile.objects.get(user=user, is_brand_manager=True)
        brand_profile = BrandProfile.objects.get(user_profile=user_profile)
        brand_profile.sustainability_story = sustainability_story
        brand_profile.save()
        
        return brand_profile
    
    @transaction.atomic
    def delete_brand_profile(self, user):
        """
        Complex operation: Delete brand + update user profile
        """
        user_profile = UserProfile.objects.get(user=user, is_brand_manager=True)
        brand_profile = BrandProfile.objects.get(user_profile=user_profile)
        
        brand_profile.delete()
        user_profile.is_brand_manager = False
        user_profile.save()
        
        return True