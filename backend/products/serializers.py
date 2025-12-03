"""
Description: Category Serializers
 
File: serializers.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""
"""
Description: Category Serializers

File: serializers.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""

from rest_framework import serializers
from django.utils.text import slugify
import os
import logging
from .models import Category
from .services import CategoryService, BusinessException
from .constants import *

logger = logging.getLogger(__name__)


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    Handles serialization/deserialization and validation
    """
    
    # Read-only fields for response
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'image_url']
        read_only_fields = ['id', 'image_url']
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
            'image': {'required': False}
        }
    
    def get_image_url(self, obj):
        """Return full URL for the image if it exists"""
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def validate_name(self, value):
        """Validate category name"""
        if len(value) < CATEGORY_NAME_MIN_LENGTH:
            raise serializers.ValidationError(VALIDATION_CATEGORY_NAME_TOO_SHORT)
        if len(value) > CATEGORY_NAME_MAX_LENGTH:
            raise serializers.ValidationError(VALIDATION_CATEGORY_NAME_TOO_LONG)
        return value
    
    def validate_slug(self, value):
        """Validate slug"""
        if value and Category.objects.filter(slug=value).exists():
            if self.instance:
                if Category.objects.filter(slug=value).exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError(VALIDATION_CATEGORY_SLUG_EXISTS)
            else:
                raise serializers.ValidationError(VALIDATION_CATEGORY_SLUG_EXISTS)
        return value
    
    def validate(self, data):
        """Custom validation for category data"""
        # Generate slug from name if not provided
        if not data.get('slug') and data.get('name'):
            data['slug'] = slugify(data['name'])
        
        # Validate slug is not empty
        if data.get('slug', '').strip() == '':
            raise serializers.ValidationError({
                'slug': 'Slug cannot be empty.'
            })
        
        return data
    
    def create(self, validated_data):
        """Create category using service layer"""
        try:
            category = CategoryService.create_category(validated_data)
            return category
        except BusinessException as e:
            # Convert BusinessException to serializer validation error
            raise serializers.ValidationError(e.details)
    
    def update(self, instance, validated_data):
        """Update category using service layer"""
        try:
            updated_category = CategoryService.update_category(instance, validated_data)
            return updated_category
        except BusinessException as e:
            # Convert BusinessException to serializer validation error
            raise serializers.ValidationError(e.details)


class CategoryImageSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for updating category image
    """
    image = serializers.ImageField(
        required=True,
        help_text="New image for the category"
    )
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['image', 'image_url']
        read_only_fields = ['image_url']
    
    def get_image_url(self, obj):
        """Return full URL for the image"""
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def validate_image(self, value):
        """Validate the uploaded image"""
        # Check file size
        if value.size > CATEGORY_IMAGE_MAX_SIZE_BYTES:
            raise serializers.ValidationError(
                VALIDATION_CATEGORY_IMAGE_TOO_LARGE
            )
        
        # Check file type
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in CATEGORY_IMAGE_ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                VALIDATION_CATEGORY_IMAGE_INVALID_FORMAT
            )
        
        return value
    
    def update(self, instance, validated_data):
        """Update category image using service layer"""
        try:
            updated_category = CategoryService.update_category_image(
                instance, validated_data['image']
            )
            return updated_category
        except BusinessException as e:
            # Convert BusinessException to serializer validation error
            raise serializers.ValidationError(e.details)


class CategoryListSerializer(CategorySerializer):
    """Simplified serializer for list views"""
    class Meta(CategorySerializer.Meta):
        fields = ['id', 'name', 'slug', 'image_url']