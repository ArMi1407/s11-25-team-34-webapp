"""
Description: Catgeory Views
 
File: views.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""


from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Category
from .serializers import CategorySerializer, CategoryListSerializer, CategoryImageSerializer
from .services import CategoryService


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Category resources
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Allow parsing of multipart form data for image uploads
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    # Configure filtering and searching
    filterset_fields = ['slug']  # Fixed: removed non-existent fields
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'id']
    ordering = ['name']
    
    # Lookup field for URLs
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Optimize queryset based on action"""
        queryset = super().get_queryset()
        
        # For list actions, we can optimize
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
        
        # Get slug from URL parameters
        slug = self.kwargs.get('slug')
        if slug:
            obj = get_object_or_404(queryset, slug=slug)
        else:
            # Fallback to pk
            obj = super().get_object()
        
        self.check_object_permissions(self.request, obj)
        return obj
    
    def destroy(self, request, *args, **kwargs):
        """Delete a category with additional checks"""
        category = self.get_object()
        
        # Check if category has products before deleting
        product_count = category.product_set.count()
        if product_count > 0:
            return Response(
                {
                    'detail': f'Cannot delete category with {product_count} products. '
                             f'Remove or reassign products first.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)
    

    @action(detail=True, methods=['delete'], url_path='remove-image')
    def remove_image(self, request, slug=None):
        """
        Custom action to remove category image
        DELETE /api/categories/{slug}/remove-image/
        """
        category = self.get_object()
        
        success, error_message = CategoryService.delete_category_image(category)
        
        if success:
            return Response(
                {'detail': 'Image removed successfully.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'detail': error_message or 'Failed to remove image.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['put', 'patch'], url_path='upload-image', 
            parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, slug=None):
        """
        Custom action to upload/update category image
        PUT/PATCH /api/categories/{slug}/upload-image/
        
        Expected form data: {'image': <file>}
        """
        category = self.get_object()
        
        # Usar el serializer específico para imágenes
        serializer = CategoryImageSerializer(
            category, 
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'detail': 'Image uploaded successfully.',
                    'image_url': serializer.data['image_url']
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                'detail': 'Failed to upload image.',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Custom search endpoint for categories
        GET /api/categories/search/?q={query}
        """
        query = request.query_params.get('q', '').strip()
        
        if len(query) < 2:
            return Response(
                {'detail': 'Search query must be at least 2 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use service for search logic
        categories = CategoryService.search_categories(query)
        
        # Paginate if needed
        page = self.paginate_queryset(categories)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get category statistics
        GET /api/categories/stats/
        """
        total_categories = Category.objects.count()
        categories_with_images = Category.objects.exclude(image='').count()
        
        return Response({
            'total_categories': total_categories,
            'categories_with_images': categories_with_images,
            'categories_without_images': total_categories - categories_with_images
        })