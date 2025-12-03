"""
Description: Category Serializers
 
File: serializers.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""


from rest_framework import serializers
from django.utils.text import slugify
from .models import Category
from .services import CategoryService


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
        
        # Ensure slug is unique (handled by model, but we check anyway)
        if 'slug' in data:
            existing = Category.objects.filter(slug=data['slug'])
            if self.instance:  # Update case
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise serializers.ValidationError({
                    'slug': 'A category with this slug already exists.'
                })
        
        return data
    
    def validate_name(self, value):
        """Validate category name"""
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("Name cannot exceed 100 characters.")
        return value
    
    def create(self, validated_data):
        """Create category using service layer"""
        
        
        category, errors = CategoryService.create_category(validated_data)
        if errors:
            raise serializers.ValidationError(errors)
        return category
    
    def update(self, instance, validated_data):
        """Update category using service layer"""
        
        
        updated_category, errors = CategoryService.update_category(instance, validated_data)
        if errors:
            raise serializers.ValidationError(errors)
        return updated_category

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
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Image size cannot exceed 5MB. Current size: {value.size / 1024 / 1024:.2f}MB"
            )
        
        # Check file type
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format. Supported formats: {', '.join(valid_extensions)}"
            )
        
        return value
    
    def update(self, instance, validated_data):
        """Update category image using service layer"""
        from .services import CategoryService
        
        updated_category, errors = CategoryService.update_category_image(
            instance, validated_data['image']
        )
        if errors:
            raise serializers.ValidationError(errors)
        return updated_category

class CategoryListSerializer(CategorySerializer):
    """Simplified serializer for list views"""
    class Meta(CategorySerializer.Meta):
        fields = ['id', 'name', 'slug', 'image_url']