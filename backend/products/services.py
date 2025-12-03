"""
Description: Category Services
 
File: services.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""

"""
Description: Category Services

File: services.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""

import logging
from typing import Dict, Any
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify
from cloudinary.exceptions import Error as CloudinaryError
from .models import Category
from .constants import *

logger = logging.getLogger(__name__)


class BusinessException(Exception):
    """Custom exception for business logic errors"""
    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


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
