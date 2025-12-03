"""
Description: Category Services
 
File: services.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""


import logging
from typing import Optional, Dict, Any, Tuple
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.text import slugify
from cloudinary.exceptions import Error as CloudinaryError
from .models import Category

logger = logging.getLogger(__name__)


class CategoryService:
    """
    Service layer for Category business logic
    Handles complex operations and data validation
    """
    @staticmethod
    def _validate_category_data(data: Dict[str, Any]) -> Tuple[bool, Dict]:
        """Validate category data before processing"""
        errors = {}
        
        # Name validation
        name = data.get('name', '').strip()
        if not name or len(name) < 2:
            errors['name'] = 'Name must be at least 2 characters long.'
        elif len(name) > 100:
            errors['name'] = 'Name cannot exceed 100 characters.'
        
        # Slug generation if not provided
        if 'slug' not in data or not data['slug']:
            data['slug'] = slugify(name)
        
        # Slug uniqueness (check happens at model level, but we can pre-check)
        if 'slug' in data:
            slug = data['slug']
            existing = Category.objects.filter(slug=slug)
            if 'id' in data:  # Update case
                existing = existing.exclude(pk=data['id'])
            if existing.exists():
                errors['slug'] = 'A category with this slug already exists.'
        
        return len(errors) == 0, errors
    

    @staticmethod
    def create_category(data: Dict[str, Any]) -> Tuple[Optional[Category], Dict]:
        """
        Create a new category with validation
        Returns: (category_instance, errors_dict)
        """
        is_valid, errors = CategoryService._validate_category_data(data)
        if not is_valid:
            return None, errors
            
        try:
            with transaction.atomic():
             
                category = Category.objects.create(**data)
                logger.info(f"Category created successfully: {category.name}")
                return category, {}
                
        except Exception as e:
            logger.error(f"Error creating category: {str(e)}")
            return None, {'error': str(e)}
    
    @staticmethod
    def update_category(category, data: Dict[str, Any]) -> Tuple[Optional[Category], Dict]:
        """
        Update an existing category
        Returns: (updated_category, errors_dict)
        """
         # Add id for validation
        data_with_id = {**data, 'id': category.id}
        is_valid, errors = CategoryService._validate_category_data(data_with_id)
        if not is_valid:
            return None, errors
        
        try:
            with transaction.atomic():
                # Handle slug update - regenerate if name changes
                if 'name' in data and data['name'] != category.name:
                    if 'slug' not in data or not data['slug']:
                        data['slug'] = slugify(data['name'])
                
                for field, value in data.items():
                    setattr(category, field, value)
                
                category.full_clean()
                category.save()
                
                logger.info(f"Category updated successfully: {category.name}")
                return category, {}
                
        except ValidationError as ve:
            logger.error(f"Validation error updating category: {ve.message_dict}")
            return None, ve.message_dict
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            return None, {'error': str(e)}
    
    @staticmethod
    def update_category_image(category: Category, image_file) -> Tuple[Optional[Category], Dict]:
        """
        Update category image
        Returns: (updated_category, errors_dict)
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
                return category, {}
                
        except ValidationError as ve:
            logger.error(f"Validation error updating category image: {ve.message_dict}")
            return None, ve.message_dict
        except CloudinaryError as ce:
            logger.error(f"Cloudinary error updating image: {str(ce)}")
            return None, {'image': 'Error uploading image to cloud storage'}
        except Exception as e:
            logger.error(f"Error updating category image: {str(e)}")
            return None, {'error': str(e)}
    
    @staticmethod
    def delete_category_image(category) -> Tuple[bool, Optional[str]]:
        """
        Delete category image if exists
        Returns: (success_bool, error_message)
        """
        if not category.image:
            return True, None
        
        try:
            # Delete the image file
            category.image.delete(save=False)
            # Clear the field
            category.image = None
            category.save(update_fields=['image'])
            
            logger.info(f"Image removed from category: {category.name}")
            return True, None
        
        except CloudinaryError as ce:
            logger.error(f"Cloudinary error deleting image: {str(ce)}")
            return False, "Error deleting image from cloud storage"
        except Exception as e:
            logger.error(f"Error deleting category image: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def search_categories(query: str, limit: int = 50) -> list:
        """Search categories by name or description"""
        from django.db.models import Q
        
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        return Category.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        ).order_by('name')[:limit]