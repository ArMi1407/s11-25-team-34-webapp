"""
User Profile and Brand Profile Services

File: services.py  
Author: Anthony Bañon
Created: 2025-11-29
Last Updated: 2025-11-30
Modify: Added business logic for user and brand profile management
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
    Service class for authentication and token management
    """
    
    def login_user(self, username, password):
        """
        Authenticate user and return token
        """       
        user = authenticate(username=username, password=password)
        
        if not user:
            raise BusinessException(ERROR_INVALID_CREDENTIALS)
        
        # BUSINESS RULE: Check if user is active
        if not user.is_active:
            raise BusinessException(ERROR_ACCOUNT_DEACTIVATED)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user profile
        user_profile = UserProfile.objects.get(user=user)
        
        return {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'token': token.key,
            'is_brand_manager': user_profile.is_brand_manager,
            'eco_points': user_profile.eco_points,
            'total_carbon_saved': user_profile.total_carbon_saved
        }
    
    def logout_user(self, user):
        """
        Logout user by deleting their token
        """
        try:
            Token.objects.filter(user=user).delete()
            return True
        except Exception:
            raise BusinessException("Failed to logout user")
    
    @transaction.atomic
    def change_password(self, user_id, current_password, new_password):
        """
        Change user password and delete all tokens
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Verify current password
            if not user.check_password(current_password):
                raise BusinessException(ERROR_INVALID_CREDENTIALS)
            
            # Validate new password
            try:
                validate_password(new_password, user)
            except ValidationError as e:
                raise BusinessException(str(e))
            
            # Set new password and save
            user.set_password(new_password)
            user.save()
            
            # Delete all tokens to force re-login
            Token.objects.filter(user=user).delete()
            
            return True
            
        except User.DoesNotExist:
            raise BusinessException(ERROR_USER_NOT_FOUND)



class UserProfileService:
    """
    Service class for UserProfile business logic and operations
    """

    @transaction.atomic
    def register_user(self, user_data, profile_data=None):
        """
        Register a new user with token authentication
        ASSUMES data has been validated by serializer
        """
        # BUSINESS RULE: Check if user already exists (redundant but safe)
        if User.objects.filter(username=user_data['username']).exists():
            raise BusinessException(ERROR_USERNAME_EXISTS)
        
        if User.objects.filter(email=user_data['email']).exists():
            raise BusinessException(ERROR_EMAIL_EXISTS)
        
        # Create user (password hashing happens automatically in create_user)
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        # Create user profile
        profile_data = profile_data or {}
        UserProfile.objects.create(
            user=user,
            phone=profile_data.get('phone', ''),
            eco_points=profile_data.get('eco_points', DEFAULT_ECO_POINTS),
            total_carbon_saved=profile_data.get('total_carbon_saved', DEFAULT_CARBON_SAVED),
            is_brand_manager=profile_data.get('is_brand_manager', False)
        )
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return {
            'user_id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'token': token.key,
            'is_brand_manager': profile_data.get('is_brand_manager', False)
        }
    
    def get_user_profile(self, user_id):
        """
        Get complete user profile with eco stats
        """
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            
            profile_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user_profile.phone,
                'eco_points': user_profile.eco_points,
                'total_carbon_saved': user_profile.total_carbon_saved,
                'is_brand_manager': user_profile.is_brand_manager,
                'date_joined': user.date_joined
            }
            
            # Add brand info if user is brand manager
            if user_profile.is_brand_manager:
                try:
                    brand_profile = BrandProfile.objects.get(user_profile=user_profile)
                    profile_data.update({
                        'brand_id': brand_profile.id,
                        'brand_name': brand_profile.brand_name,
                        'sustainability_story': brand_profile.sustainability_story
                    })
                except BrandProfile.DoesNotExist:
                    # BUSINESS RULE: Brand manager must have brand profile
                    raise BusinessException(ERROR_BRAND_NOT_FOUND)
            
            return profile_data
            
        except User.DoesNotExist:
            raise BusinessException(ERROR_USER_NOT_FOUND)
        except UserProfile.DoesNotExist:
            raise BusinessException(ERROR_PROFILE_NOT_FOUND)
        
    @transaction.atomic
    def update_user_profile(self, user_id, validated_data):
        """
        Update user profile information with validated data
        """
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            
            # Actualizar campos del User
            if 'first_name' in validated_data:
                user.first_name = validated_data['first_name']
            if 'last_name' in validated_data:
                user.last_name = validated_data['last_name']
            user.save()
            
            # Actualizar campos del UserProfile
            if 'phone' in validated_data:
                user_profile.phone = validated_data['phone']
            user_profile.save()
            
            return self.get_user_profile(user_id)
            
        except User.DoesNotExist:
            raise BusinessException(ERROR_USER_NOT_FOUND)
        except UserProfile.DoesNotExist:
            raise BusinessException(ERROR_PROFILE_NOT_FOUND)
    
    @transaction.atomic
    def update_eco_points(self, user_id, points_to_add, carbon_saved=MIN_CARBON_SAVED):
        """
        Update user's eco points and carbon saved totals
        """
        # BUSINESS RULE: Points must be reasonable
        if abs(points_to_add) > MAX_ECO_POINTS_ADDITION:
            raise BusinessException(ERROR_POINTS_EXCEED_LIMIT)
        
        # BUSINESS RULE: Carbon saved must be reasonable  
        if abs(carbon_saved) > MAX_CARBON_SAVED_ADDITION:
            raise BusinessException(ERROR_CARBON_EXCEED_LIMIT)
        
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            user_profile.eco_points += points_to_add
            user_profile.total_carbon_saved += carbon_saved
            
            # BUSINESS RULE: Values can't go negative
            user_profile.eco_points = max(MIN_ECO_POINTS, user_profile.eco_points)
            user_profile.total_carbon_saved = max(MIN_CARBON_SAVED, user_profile.total_carbon_saved)
            
            user_profile.save()
            
            return {
                'eco_points': user_profile.eco_points,
                'total_carbon_saved': user_profile.total_carbon_saved,
                'points_added': points_to_add,
                'carbon_saved_added': carbon_saved
            }
            
        except UserProfile.DoesNotExist:
            raise BusinessException(ERROR_PROFILE_NOT_FOUND)
    
    
    @transaction.atomic
    def delete_user(self, user_id):
        """
        Delete user account and all associated data
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Delete tokens
            Token.objects.filter(user=user).delete()
            
            # Delete brand profile if exists
            try:
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.is_brand_manager:
                    BrandProfile.objects.filter(user_profile=user_profile).delete()
                # Delete user profile
                user_profile.delete()
            except UserProfile.DoesNotExist:
                pass  # No profile to delete
            
            # Delete user
            user.delete()
            
            return True
            
        except User.DoesNotExist:
            raise BusinessException(ERROR_USER_NOT_FOUND)





class BrandProfileService:
    """
    Service class for BrandProfile business logic and operations
    """
    @transaction.atomic
    def create_brand_manager(self, user_data, brand_data):
        """
        Create a brand manager user with brand profile and authentication
        """
        # BUSINESS RULE: Brand name must be unique
        if BrandProfile.objects.filter(brand_name__iexact=brand_data['brand_name']).exists():
            raise BusinessException(ERROR_BRAND_NAME_EXISTS)
        
        # Use AuthService to register user
        profile_data = {'is_brand_manager': True}
        auth_service = AuthService()
        user_response = auth_service.register_user(user_data, profile_data)
        
        # Get the user profile
        user = User.objects.get(id=user_response['user_id'])
        user_profile = UserProfile.objects.get(user=user)
        
        # Create brand profile
        brand_profile = BrandProfile.objects.create(
            user_profile=user_profile,
            brand_name=brand_data['brand_name'],
            sustainability_story=brand_data.get('sustainability_story', '')
        )
        
        # Add brand info to response
        user_response.update({
            'brand_id': brand_profile.id,
            'brand_name': brand_profile.brand_name,
            'sustainability_story': brand_profile.sustainability_story
        })
        
        return user_response
    
    def get_brand_profile(self, user_id):
        """
        Get complete brand profile by user ID
        """
        try:
            user_profile = UserProfile.objects.get(user_id=user_id, is_brand_manager=True)
            brand_profile = BrandProfile.objects.get(user_profile=user_profile)
            
            return {
                'brand_id': brand_profile.id,
                'brand_name': brand_profile.brand_name,
                'sustainability_story': brand_profile.sustainability_story,
                'manager_name': f"{user_profile.user.first_name} {user_profile.user.last_name}",
                'manager_email': user_profile.user.email,
                'manager_phone': user_profile.phone
            }
        except UserProfile.DoesNotExist:
            raise BusinessException(ERROR_NOT_BRAND_MANAGER)
        except BrandProfile.DoesNotExist:
            raise BusinessException(ERROR_BRAND_NOT_FOUND)

    @transaction.atomic
    def update_brand_story(self, user_id, sustainability_story):
        """
        Update brand sustainability story with user authentication
        """
        # BUSINESS RULE: Story length limit
        if len(sustainability_story) > MAX_SUSTAINABILITY_STORY_LENGTH:
            raise BusinessException(ERROR_STORY_EXCEED_LENGTH)
        
        try:
            user_profile = UserProfile.objects.get(user_id=user_id, is_brand_manager=True)
            brand_profile = BrandProfile.objects.get(user_profile=user_profile)
            brand_profile.sustainability_story = sustainability_story
            brand_profile.save()
            return brand_profile
        except UserProfile.DoesNotExist:
            raise BusinessException(ERROR_NOT_BRAND_MANAGER)
        except BrandProfile.DoesNotExist:
            raise BusinessException(ERROR_BRAND_NOT_FOUND)
    
    @transaction.atomic
    def delete_brand_profile(self, user_id):
        """
        Delete brand profile (user remains)
        """
        try:
            user_profile = UserProfile.objects.get(user_id=user_id, is_brand_manager=True)
            brand_profile = BrandProfile.objects.get(user_profile=user_profile)
            brand_profile.delete()
            return True
        except UserProfile.DoesNotExist:
            raise BusinessException(ERROR_NOT_BRAND_MANAGER)
        except BrandProfile.DoesNotExist:
            raise BusinessException(ERROR_BRAND_NOT_FOUND)


# Service instances for easy import
auth_service = AuthService()
user_profile_service = UserProfileService()
brand_profile_service = BrandProfileService()