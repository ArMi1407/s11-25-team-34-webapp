"""
Description: Category Services
 
File: services.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-05
Changes: Switching to a single image for product
"""

import logging
from typing import Dict, Any
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify
from cloudinary.exceptions import Error as CloudinaryError
from .models import Category, Product
from accounts.models import BrandProfile
from .constants import *


logger = logging.getLogger(__name__)


class BusinessException(Exception):
    """Custom exception for business logic errors"""
    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

######### Category Services #########

class CategoryService:
    """
    Service layer for Category business logic
    Handles complex operations and data validation
    """
    
    @staticmethod
    def create_category(data: Dict[str, Any]) -> Category:
        """
        Create a new category with validation
        Returns: category_instance
        Raises: BusinessException on error
        """
        try:
            with transaction.atomic():
                # Auto-generate slug if not provided
                if 'slug' not in data or not data['slug']:
                    data['slug'] = slugify(data.get('name', ''))
                
                # Check slug uniqueness
                slug = data.get('slug')
                if slug and Category.objects.filter(slug=slug).exists():
                    raise BusinessException(
                        VALIDATION_CATEGORY_SLUG_EXISTS,
                        error_code='SLUG_EXISTS',
                        details={'slug': slug}
                    )
                
                category = Category.objects.create(**data)
                logger.info(f"Category created successfully: {category.name} (ID: {category.id})")
                return category
                
        except ValidationError as ve:
            logger.error(f"Validation error creating category: {ve.message_dict}")
            raise BusinessException(
                ERROR_CATEGORY_CREATE_FAILED,
                error_code='VALIDATION_ERROR',
                details=ve.message_dict
            )
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            raise BusinessException(
                ERROR_CATEGORY_CREATE_FAILED,
                error_code='CREATE_ERROR',
                details={'error': str(e)}
            )
    
    @staticmethod
    def update_category(category: Category, data: Dict[str, Any]) -> Category:
        """
        Update an existing category
        Returns: updated_category
        Raises: BusinessException on error
        """
        try:
            with transaction.atomic():
                # Handle slug update - regenerate if name changes
                if 'name' in data and data['name'] != category.name:
                    if 'slug' not in data or not data['slug']:
                        data['slug'] = slugify(data['name'])
                
                # Check slug uniqueness (excluding current category)
                if 'slug' in data:
                    slug = data['slug']
                    if Category.objects.filter(slug=slug).exclude(pk=category.id).exists():
                        raise BusinessException(
                            VALIDATION_CATEGORY_SLUG_EXISTS,
                            error_code='SLUG_EXISTS',
                            details={'slug': slug}
                        )
                
                for field, value in data.items():
                    setattr(category, field, value)
                
                category.full_clean()
                category.save()
                
                logger.info(f"Category updated successfully: {category.name} (ID: {category.id})")
                return category
                
        except ValidationError as ve:
            logger.error(f"Validation error updating category: {ve.message_dict}")
            raise BusinessException(
                ERROR_CATEGORY_UPDATE_FAILED,
                error_code='VALIDATION_ERROR',
                details=ve.message_dict
            )
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            raise BusinessException(
                ERROR_CATEGORY_UPDATE_FAILED,
                error_code='UPDATE_ERROR',
                details={'error': str(e)}
            )
    
    @staticmethod
    def update_category_image(category: Category, image_file) -> Category:
        """
        Update category image
        Returns: updated_category
        Raises: BusinessException on error
        """
        try:
            with transaction.atomic():
                # Delete old image if exists
                if category.image:
                    try:
                        category.image.delete(save=False)
                    except Exception as e:
                        logger.warning(f"Could not delete old image: {str(e)}")
                
                # Save new image
                category.image = image_file
                category.full_clean()
                category.save(update_fields=['image'])
                
                logger.info(f"Image updated for category: {category.name} (ID: {category.id})")
                return category
                
        except ValidationError as ve:
            logger.error(f"Validation error updating category image: {ve.message_dict}")
            raise BusinessException(
                ERROR_CATEGORY_IMAGE_UPLOAD_FAILED,
                error_code='VALIDATION_ERROR',
                details=ve.message_dict
            )
        except CloudinaryError as ce:
            logger.error(f"Cloudinary error updating image: {str(ce)}")
            raise BusinessException(
                ERROR_CATEGORY_CLOUDINARY_ERROR,
                error_code='CLOUDINARY_ERROR',
                details={'error': str(ce)}
            )
        except Exception as e:
            logger.error(f"Error updating category image: {str(e)}")
            raise BusinessException(
                ERROR_CATEGORY_IMAGE_UPLOAD_FAILED,
                error_code='IMAGE_UPDATE_ERROR',
                details={'error': str(e)}
            )
    
    @staticmethod
    def delete_category_image(category: Category) -> None:
        """
        Delete category image if exists
        Raises: BusinessException on error
        """
        if not category.image:
            logger.info(f"No image to delete for category: {category.name}")
            return
        
        try:
            # Delete the image file
            category.image.delete(save=False)
            # Clear the field
            category.image = None
            category.save(update_fields=['image'])
            
            logger.info(f"Image removed from category: {category.name}")
            
        except CloudinaryError as ce:
            logger.error(f"Cloudinary error deleting image: {str(ce)}")
            raise BusinessException(
                ERROR_CATEGORY_CLOUDINARY_ERROR,
                error_code='CLOUDINARY_ERROR',
                details={'error': str(ce)}
            )
        except Exception as e:
            logger.error(f"Error deleting category image: {str(e)}")
            raise BusinessException(
                ERROR_CATEGORY_IMAGE_DELETE_FAILED,
                error_code='IMAGE_DELETE_ERROR',
                details={'error': str(e)}
            )
    
    @staticmethod
    def delete_category(category: Category) -> None:
        """
        Delete a category with business rule checks
        Raises: BusinessException on error
        """
        # Check if category has products before deleting
        product_count = category.product_set.count()
        if product_count > 0:
            raise BusinessException(
                ERROR_CATEGORY_HAS_PRODUCTS,
                error_code='HAS_PRODUCTS',
                details={'product_count': product_count}
            )
        
        try:
            # Delete associated image if exists
            if category.image:
                category.image.delete(save=False)
            
            category.delete()
            logger.info(f"Category deleted: {category.name} (ID: {category.id})")
            
        except Exception as e:
            logger.error(f"Error deleting category: {str(e)}")
            raise BusinessException(
                "Failed to delete category",
                error_code='DELETE_ERROR',
                details={'error': str(e)}
            )

######### Product Services #########

class ProductService:
    """
    Service layer for Product business logic
    Handles complex operations and data validation
    """
    
    @staticmethod
    def calculate_carbon_footprint(
        base_type: str,
        packaging_material: str,
        weight: int,
        transportation_type: str,
        origin_country: str,
        recyclable_packaging: bool
    ) -> float:
        """
        Calculate carbon footprint based on product characteristics
        Returns: carbon footprint in kg CO2
        """
        try:
            # Base carbon factors (kg CO2 per gram)
            base_factors = {
                'water_based': 0.0015,
                'plant_based': 0.0010,
                'oil_based': 0.0020
            }
            
            # Packaging carbon factors (kg CO2 per gram)
            packaging_factors = {
                'plastic_bottle': 0.0025,
                'plastic_tube': 0.0020,
                'glass_container': 0.0015,
                'paper_wrap': 0.0005
            }
            
            # Transportation carbon factors (kg CO2 per gram per km)
            transportation_factors = {
                'air': 0.0005,
                'sea': 0.00005,
                'land': 0.0001
            }
            
            # Calculate base material footprint
            base_factor = base_factors.get(base_type, 0.0015)
            base_footprint = base_factor * weight
            
            # Calculate packaging footprint
            packaging_factor = packaging_factors.get(packaging_material, 0.0020)
            packaging_footprint = packaging_factor * (weight * 0.1)  # Estimate packaging weight
            
            # Apply recyclable packaging discount
            if recyclable_packaging:
                packaging_footprint *= 0.7  # 30% reduction for recyclable
            
            # Calculate transportation footprint (simplified)
            distance = 1000  # km - would be calculated based on origin_country
            transport_factor = transportation_factors.get(transportation_type, 0.0001)
            transport_footprint = transport_factor * weight * distance
            
            # Total carbon footprint
            total_footprint = base_footprint + packaging_footprint + transport_footprint
            
            # Round to 2 decimal places
            return round(total_footprint, 2)
            
        except Exception as e:
            logger.error(f"Error calculating carbon footprint: {str(e)}")
            return PRODUCT_DEFAULT_CARBON_FOOTPRINT
    
    @staticmethod
    def determine_eco_badge(carbon_footprint: float) -> str:
        """
        Determine eco badge based on carbon footprint
        """
        if carbon_footprint <= ECO_BADGE_THRESHOLD_LOW:
            return '🌱 low Impact'
        elif carbon_footprint <= ECO_BADGE_THRESHOLD_MEDIUM:
            return '🌿 medium Impact'
        else:
            return '🌳 high Impact'
    
    @staticmethod
    def create_product(data: Dict[str, Any], brand: BrandProfile, image=None) -> Product:
        """
        Create a new product with single image
        Returns: product_instance
        Raises: BusinessException on error
        """
        try:
            with transaction.atomic():
                # Auto-generate slug if not provided (trust serializer validation)
                if 'slug' not in data or not data['slug']:
                    data['slug'] = slugify(data.get('name', ''))
                
                # Check slug uniqueness
                slug = data.get('slug')
                if slug and Product.objects.filter(slug=slug).exists():
                    raise BusinessException(
                        "Product with this slug already exists",
                        error_code='SLUG_EXISTS',
                        details={'slug': slug}
                    )
                
                # Calculate carbon footprint if not provided
                if 'carbon_footprint' not in data or not data['carbon_footprint']:
                    data['carbon_footprint'] = ProductService.calculate_carbon_footprint(
                        base_type=data.get('base_type'),
                        packaging_material=data.get('packaging_material'),
                        weight=data.get('weight', 0),
                        transportation_type=data.get('transportation_type'),
                        origin_country=data.get('origin_country'),
                        recyclable_packaging=data.get('recyclable_packaging', True)
                    )
                
                # Determine eco badge
                if 'eco_badge' not in data or not data['eco_badge']:
                    data['eco_badge'] = ProductService.determine_eco_badge(
                        data.get('carbon_footprint', 0.0)
                    )
                
                # Create product
                product = Product.objects.create(brand=brand, **data)
                
                # Handle image if provided
                if image:
                    product.image = image
                    product.save()
                
                logger.info(f"Product created successfully: {product.name} (ID: {product.id})")
                return product
                
        except ValidationError as ve:
            logger.error(f"Validation error creating product: {ve.message_dict}")
            raise BusinessException(
                ERROR_PRODUCT_CREATE_FAILED,
                error_code='VALIDATION_ERROR',
                details=ve.message_dict
            )
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise BusinessException(
                ERROR_PRODUCT_CREATE_FAILED,
                error_code='CREATE_ERROR',
                details={'error': str(e)}
            )
    
    @staticmethod
    def update_product(product: Product, data: Dict[str, Any], image=None) -> Product:
        """
        Update an existing product with optional image
        Returns: updated_product
        Raises: BusinessException on error
        """
        try:
            with transaction.atomic():
                # Handle slug update - regenerate if name changes
                if 'name' in data and data['name'] != product.name:
                    if 'slug' not in data or not data['slug']:
                        data['slug'] = slugify(data['name'])
                
                # Check slug uniqueness (excluding current product)
                if 'slug' in data:
                    slug = data['slug']
                    if Product.objects.filter(slug=slug).exclude(pk=product.id).exists():
                        raise BusinessException(
                            "Product with this slug already exists",
                            error_code='SLUG_EXISTS',
                            details={'slug': slug}
                        )
                
                # Recalculate carbon footprint if environmental data changes
                environmental_fields = ['base_type', 'packaging_material', 'weight', 
                                      'transportation_type', 'origin_country', 'recyclable_packaging']
                
                if any(field in data for field in environmental_fields):
                    # Use updated values or existing values
                    base_type = data.get('base_type', product.base_type)
                    packaging_material = data.get('packaging_material', product.packaging_material)
                    weight = data.get('weight', product.weight)
                    transportation_type = data.get('transportation_type', product.transportation_type)
                    origin_country = data.get('origin_country', product.origin_country)
                    recyclable_packaging = data.get('recyclable_packaging', product.recyclable_packaging)
                    
                    data['carbon_footprint'] = ProductService.calculate_carbon_footprint(
                        base_type=base_type,
                        packaging_material=packaging_material,
                        weight=weight,
                        transportation_type=transportation_type,
                        origin_country=origin_country,
                        recyclable_packaging=recyclable_packaging
                    )
                    
                    # Update eco badge
                    data['eco_badge'] = ProductService.determine_eco_badge(
                        data['carbon_footprint']
                    )
                
                # Update product fields
                for field, value in data.items():
                    setattr(product, field, value)
                
                # Handle image update
                if image is not None:
                    # Delete old image file if exists
                    if product.image:
                        try:
                            product.image.delete(save=False)
                        except Exception as e:
                            logger.warning(f"Could not delete old image: {str(e)}")
                    
                    product.image = image
                
                product.full_clean()
                product.save()
                
                logger.info(f"Product updated successfully: {product.name} (ID: {product.id})")
                return product
                
        except ValidationError as ve:
            logger.error(f"Validation error updating product: {ve.message_dict}")
            raise BusinessException(
                ERROR_PRODUCT_UPDATE_FAILED,
                error_code='VALIDATION_ERROR',
                details=ve.message_dict
            )
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            raise BusinessException(
                ERROR_PRODUCT_UPDATE_FAILED,
                error_code='UPDATE_ERROR',
                details={'error': str(e)}
            )
    
    @staticmethod
    def delete_product(product: Product, user) -> None:
        """
        Delete a product with permission check
        Raises: BusinessException on error
        """
        try:
            # Check if product belongs to user's brand
            if product.brand.user_profile.user != user:
                raise BusinessException(
                    ERROR_PRODUCT_BRAND_MISMATCH,
                    error_code='PERMISSION_DENIED'
                )
            
            # Delete associated image file
            if product.image:
                try:
                    product.image.delete(save=False)
                except Exception as e:
                    logger.warning(f"Could not delete product image: {str(e)}")
            
            product.delete()
            logger.info(f"Product deleted: {product.name} (ID: {product.id})")
            
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            raise BusinessException(
                ERROR_PRODUCT_DELETE_FAILED,
                error_code='DELETE_ERROR',
                details={'error': str(e)}
            )
    