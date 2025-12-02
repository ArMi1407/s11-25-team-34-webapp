"""
Serializers ONLY for validation and formatting

File: serializers.py
Author: Anthony Bañon  
Created: 2025-12-01
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, BrandProfile
from .constants import *


##### Authentication Serializers #####

class UserLoginSerializer(serializers.Serializer):
    """Validation ONLY for login input"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    """Validation ONLY for password change"""
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])


##### User Serializers #####

class UserRegistrationSerializer(serializers.Serializer):
    """Validation ONLY for registration"""
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=MAX_PHONE_LENGTH)
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(ERROR_USERNAME_EXISTS)
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(ERROR_EMAIL_EXISTS)
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Formatting ONLY for user profile output"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'first_name', 'last_name', 'phone',
            'eco_points', 'total_carbon_saved', 'is_brand_manager'
        ]
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.Serializer):
    """Validation ONLY for profile update"""
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=MAX_NAME_LENGTH)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=MAX_NAME_LENGTH)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=MAX_PHONE_LENGTH)


class EcoPointsUpdateSerializer(serializers.Serializer):
    """Validation ONLY for eco points update"""
    points = serializers.IntegerField(required=True)
    carbon_saved = serializers.FloatField(required=False, default=0.0)
    
    def validate_points(self, value):
        if abs(value) > MAX_ECO_POINTS_ADDITION:
            raise serializers.ValidationError(ERROR_POINTS_EXCEED_LIMIT)
        return value
    
    def validate_carbon_saved(self, value):
        if abs(value) > MAX_CARBON_SAVED_ADDITION:
            raise serializers.ValidationError(ERROR_CARBON_EXCEED_LIMIT)
        return value


##### Brand Serializers #####

class BrandProfileSerializer(serializers.ModelSerializer):
    """Formatting ONLY for brand profile output"""
    manager_name = serializers.SerializerMethodField()
    manager_email = serializers.SerializerMethodField()
    
    class Meta:
        model = BrandProfile
        fields = ['id', 'brand_name', 'sustainability_story', 'manager_name', 'manager_email']
    
    def get_manager_name(self, obj):
        return f"{obj.user_profile.user.first_name} {obj.user_profile.user.last_name}"
    
    def get_manager_email(self, obj):
        return obj.user_profile.user.email


class BrandManagerRegistrationSerializer(UserRegistrationSerializer):
    """Validation ONLY for brand manager registration"""
    brand_name = serializers.CharField(required=True, max_length=MAX_BRAND_NAME_LENGTH)
    sustainability_story = serializers.CharField(required=False, allow_blank=True, max_length=MAX_SUSTAINABILITY_STORY_LENGTH)
    
    def validate_brand_name(self, value):
        if BrandProfile.objects.filter(brand_name__iexact=value).exists():
            raise serializers.ValidationError(ERROR_BRAND_NAME_EXISTS)
        return value


class BrandStoryUpdateSerializer(serializers.Serializer):
    """Validation ONLY for brand story update"""
    sustainability_story = serializers.CharField(required=True, max_length=MAX_SUSTAINABILITY_STORY_LENGTH)
    
    def validate_sustainability_story(self, value):
        if len(value) > MAX_SUSTAINABILITY_STORY_LENGTH:
            raise serializers.ValidationError(ERROR_STORY_EXCEED_LENGTH)
        return value