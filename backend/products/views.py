"""
Description: Catgeory Views
 
File: views.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""

"""
Description: Category Views

File: views.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer, CategoryImageSerializer
from .services import CategoryService, BusinessException
from .constants import *

import logging
logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Category resources
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    # Configure filtering and searching
    filterset_fields = ['slug']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    ordering = ['name']
    
    # Lookup field for URLs
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Optimize queryset based on action"""
        queryset = super().get_queryset()
        
        if self.action == 'list':
            queryset = queryset.only('id', 'name', 'slug', 'image')
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializer for list action"""
        if self.action == 'upload_image':
            return CategoryImageSerializer
        elif self.action == 'list':
            return CategoryListSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Override permissions for specific actions
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'remove_image', 'upload_image']:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_object(self):
        """Get category by slug"""
        queryset = self.filter_queryset(self.get_queryset())
        
        slug = self.kwargs.get('slug')
        if slug:
            obj = get_object_or_404(queryset, slug=slug)
        else:
            obj = super().get_object()
        
        self.check_object_permissions(self.request, obj)
        return obj
    
    def destroy(self, request, *args, **kwargs):
        """Delete a category"""
        category = self.get_object()
        
        try:
            CategoryService.delete_category(category)
            return Response(
                {'detail': SUCCESS_CATEGORY_DELETED},
                status=status.HTTP_200_OK
            )
        except BusinessException as e:
            return Response(
                {
                    'detail': e.message,
                    'error_code': e.error_code,
                    'details': e.details
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['delete'], url_path='remove-image')
    def remove_image(self, request, slug=None):
        """
        Custom action to remove category image
        DELETE /api/categories/{slug}/remove-image/
        """
        category = self.get_object()
        
        try:
            CategoryService.delete_category_image(category)
            return Response(
                {'detail': SUCCESS_CATEGORY_IMAGE_REMOVED},
                status=status.HTTP_200_OK
            )
        except BusinessException as e:
            return Response(
                {
                    'detail': e.message,
                    'error_code': e.error_code,
                    'details': e.details
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['put'], url_path='upload-image', 
            parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, slug=None):
        """
        Custom action to upload/update category image
        PUT/PATCH /api/categories/{slug}/upload-image/
        
        Expected form data: {'image': <file>}
        """
        category = self.get_object()
        
        serializer = CategoryImageSerializer(
            category, 
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'detail': SUCCESS_CATEGORY_IMAGE_UPLOADED,
                    'image_url': serializer.data['image_url']
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                'detail': ERROR_CATEGORY_IMAGE_UPLOAD_FAILED,
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )