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
from .models import Category, ProductImage, Category, Product, BrandProfile
from .services import CategoryService, BusinessException, ProductService
from .constants import *

logger = logging.getLogger(__name__)

##### Category Serializers #####

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

##### Product Serializers #####

class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage model
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'is_primary']
        read_only_fields = ['id', 'image_url']
    
    def get_image_url(self, obj):
        """Return full URL for the image"""
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def validate_image(self, value):
        """Validate product image"""
        # Check file size
        if value.size > PRODUCT_IMAGE_MAX_SIZE_BYTES:
            raise serializers.ValidationError(
                VALIDATION_PRODUCT_IMAGE_TOO_LARGE
            )
        
        # Check file type
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in PRODUCT_IMAGE_ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                VALIDATION_PRODUCT_IMAGE_INVALID_FORMAT
            )
        
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for product listing
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 
            'brand', 'brand_name', 'price', 'stock', 'is_active',
            'carbon_footprint', 'eco_badge', 'primary_image',
            'image_urls', 'created_at'
        ]
        read_only_fields = ['id', 'category_name', 'brand_name', 'primary_image', 'image_urls']
    
    def get_primary_image(self, obj):
        """Get primary image URL"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and hasattr(primary_image.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_image_urls(self, obj):
        """Get all image URLs"""
        urls = []
        request = self.context.get('request')
        
        for image in obj.images.all():
            if hasattr(image.image, 'url'):
                url = image.image.url
                if request:
                    url = request.build_absolute_uri(url)
                urls.append({
                    'id': image.id,
                    'url': url,
                    'is_primary': image.is_primary
                })
        
        return urls


class ProductSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Product model with nested images
    """
    images = ProductImageSerializer(many=True, required=False)
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'brand', 'brand_name', 'climatiq_category', 'price', 'stock',
            'is_active', 'ingredient_main', 'base_type', 'packaging_material',
            'origin_country', 'weight', 'recyclable_packaging', 'transportation_type',
            'carbon_footprint', 'eco_badge', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'category_name', 'brand_name', 'carbon_footprint', 
            'eco_badge', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
            'climatiq_category': {'required': False},
        }
    
    def validate_name(self, value):
        """Validate product name"""
        if len(value) < PRODUCT_NAME_MIN_LENGTH:
            raise serializers.ValidationError(VALIDATION_PRODUCT_NAME_TOO_SHORT)
        if len(value) > PRODUCT_NAME_MAX_LENGTH:
            raise serializers.ValidationError(VALIDATION_PRODUCT_NAME_TOO_LONG)
        return value
    
    def validate_description(self, value):
        """Validate product description"""
        if len(value) > PRODUCT_DESCRIPTION_MAX_LENGTH:
            raise serializers.ValidationError(VALIDATION_PRODUCT_DESCRIPTION_TOO_LONG)
        return value
    
    def validate_price(self, value):
        """Validate product price"""
        if value < PRODUCT_PRICE_MIN_VALUE:
            raise serializers.ValidationError("Price must be a positive number")
        
        # Check decimal places
        str_value = str(value)
        if '.' in str_value:
            decimal_places = len(str_value.split('.')[1])
            if decimal_places > PRODUCT_PRICE_DECIMAL_PLACES:
                raise serializers.ValidationError(
                    f"Price can have at most {PRODUCT_PRICE_DECIMAL_PLACES} decimal places"
                )
        
        # Check total digits
        digits = str_value.replace('.', '').replace('-', '')
        if len(digits) > PRODUCT_PRICE_MAX_DIGITS:
            raise serializers.ValidationError(
                f"Price can have at most {PRODUCT_PRICE_MAX_DIGITS} digits"
            )
        
        return value
    
    def validate_stock(self, value):
        """Validate product stock"""
        if value < PRODUCT_STOCK_MIN_VALUE:
            raise serializers.ValidationError(VALIDATION_PRODUCT_STOCK_INVALID)
        return value
    
    def validate_weight(self, value):
        """Validate product weight"""
        if value < PRODUCT_WEIGHT_MIN_VALUE or value > PRODUCT_WEIGHT_MAX_VALUE:
            raise serializers.ValidationError(VALIDATION_PRODUCT_WEIGHT_INVALID)
        return value
    
    def validate_origin_country(self, value):
        """Validate origin country code"""
        if len(value) != PRODUCT_ORIGIN_COUNTRY_LENGTH:
            raise serializers.ValidationError(
                f"Origin country must be a {PRODUCT_ORIGIN_COUNTRY_LENGTH}-letter ISO code"
            )
        return value.upper()
    
    def validate(self, data):
        """Custom validation for product data"""
        # Generate slug from name if not provided
        if not data.get('slug') and data.get('name'):
            data['slug'] = slugify(data['name'])
        
        # Validate required fields
        if not data.get('category'):
            raise serializers.ValidationError({
                'category': VALIDATION_PRODUCT_CATEGORY_REQUIRED
            })
        
        # Validate category exists
        if data.get('category'):
            try:
                category = Category.objects.get(id=data['category'].id)
                data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({
                    'category': ERROR_CATEGORY_NOT_FOUND
                })
        
        # Validate images have at least one primary
        images_data = data.get('images', [])
        if images_data:
            primary_count = sum(1 for img in images_data if img.get('is_primary', False))
            if primary_count == 0:
                raise serializers.ValidationError({
                    'images': VALIDATION_PRODUCT_PRIMARY_IMAGE_REQUIRED
                })
        
        return data
    
    def create(self, validated_data):
        """Create product using service layer"""
        try:
            # Extract images data
            images_data = validated_data.pop('images', [])
            
            # Get brand from context (usually from request user)
            request = self.context.get('request')
            if not request or not request.user.is_authenticated:
                raise serializers.ValidationError(AUTHENTICATION_REQUIRED)
            
            try:
                brand = request.user.brandprofile
            except BrandProfile.DoesNotExist:
                raise serializers.ValidationError("User does not have a brand profile")
            
            # Create product using service
            product = ProductService.create_product(
                data=validated_data,
                brand=brand,
                images_data=images_data
            )
            
            return product
            
        except BusinessException as e:
            raise serializers.ValidationError(e.details)
    
    def update(self, instance, validated_data):
        """Update product using service layer"""
        try:
            # Extract images data
            images_data = validated_data.pop('images', None)
            
            # Get user for permission check
            request = self.context.get('request')
            if not request or not request.user.is_authenticated:
                raise serializers.ValidationError(AUTHENTICATION_REQUIRED)
            
            # Update product using service
            product = ProductService.update_product(
                product=instance,
                data=validated_data,
                images_data=images_data
            )
            
            return product
            
        except BusinessException as e:
            raise serializers.ValidationError(e.details)


class ProductCreateSerializer(ProductSerializer):
    """
    Serializer for product creation with additional validations
    """
    class Meta(ProductSerializer.Meta):
        extra_kwargs = {
            **ProductSerializer.Meta.extra_kwargs,
            'description': {'required': True},
            'price': {'required': True},
            'category': {'required': True},
            'ingredient_main': {'required': True},
            'base_type': {'required': True},
            'packaging_material': {'required': True},
            'origin_country': {'required': True},
            'weight': {'required': True},
            'transportation_type': {'required': True},
        }
    
    def validate(self, data):
        """Additional validation for creation"""
        data = super().validate(data)
        
        # Validate brand ownership (for creation, brand comes from user)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                brand = request.user.brandprofile
                # Brand is set from user, not from input
            except BrandProfile.DoesNotExist:
                raise serializers.ValidationError({
                    'brand': "User does not have a brand profile"
                })
        
        return data