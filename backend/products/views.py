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
Last Updated: 2025-12-05
Changes: Switching to a single image for product
"""

from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Category, Product
from .serializers import CategorySerializer, CategoryListSerializer, CategoryImageSerializer, ProductSerializer, ProductListSerializer, ProductCreateSerializer, ProductImageFieldSerializer
from .services import CategoryService, ProductService, BusinessException
from .constants import *
from .filters import ProductFilter
from rest_framework.exceptions import ValidationError


import logging
logger = logging.getLogger(__name__)

######## Category Views #####

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

######## Product Views #####

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product resources
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    # Configure filtering and searching
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'ingredient_main']
    ordering_fields = ['name', 'price', 'created_at', 'carbon_footprint']
    ordering = ['-created_at']
    
    # Lookup field for URLs
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Optimize queryset based on action and user"""
        queryset = super().get_queryset()
        
        # Filter by active status for non-authenticated users or list views
        if self.action == 'list' or not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        
        # For brand owners, show all their products
        if self.request.user.is_authenticated and hasattr(self.request.user, 'userprofile') and hasattr(self.request.user.userprofile, 'brandprofile'):
            if self.action in ['my_products', 'update', 'partial_update', 'destroy']:
                # For specific actions, include inactive products for brand owners
                queryset = queryset.filter(brand=self.request.user.userprofile.brandprofile)
            elif self.action == 'list':
                # In list view, brand owners see their inactive products too
                if self.request.query_params.get('my_products') == 'true':
                    queryset = queryset.filter(brand=self.request.user.userprofile.brandprofile)
        
        # Optimize queries - remove prefetch_related('images') as we now have single image
        if self.action == 'list':
            queryset = queryset.select_related('category', 'brand')
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializer based on action"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        elif self.action == 'upload_image':
            return ProductImageFieldSerializer  # <-- AÑADE ESTA LÍNEA
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Override permissions for specific actions
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_products', 'remove_image', 'upload_image']:
            return [IsAuthenticated()]
        return super().get_permissions()
    
    def get_object(self):
        """Get product by slug with permission check"""
        queryset = self.filter_queryset(self.get_queryset())
        
        slug = self.kwargs.get('slug')
        if slug:
            obj = get_object_or_404(queryset, slug=slug)
        else:
            obj = super().get_object()
        
        self.check_object_permissions(self.request, obj)
        return obj
    
    def create(self, request, *args, **kwargs):
        """Create a new product"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Create product through serializer which calls ProductService
            product = serializer.save()
            
            return Response(
                {
                    'detail': SUCCESS_PRODUCT_CREATED,
                    'product': ProductSerializer(product, context={'request': request}).data
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as ve:
            logger.error(f"Validation error creating product: {ve}")
            return Response(
                {
                    'detail': ERROR_PRODUCT_CREATE_FAILED,
                    'errors': ve.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            return Response(
                {
                    'detail': ERROR_PRODUCT_CREATE_FAILED,
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update a product with permission check"""
        product = self.get_object()
        
        # Check if product belongs to user's brand
        if not hasattr(request.user, 'userprofile') or not hasattr(request.user.userprofile, 'brandprofile') or product.brand != request.user.userprofile.brandprofile:
            return Response(
                {'detail': ERROR_PRODUCT_BRAND_MISMATCH},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(product, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            # Update product through serializer which calls ProductService
            updated_product = serializer.save()
            
            return Response(
                {
                    'detail': SUCCESS_PRODUCT_UPDATED,
                    'product': ProductSerializer(updated_product, context={'request': request}).data
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as ve:
            logger.error(f"Validation error updating product: {ve}")
            return Response(
                {
                    'detail': ERROR_PRODUCT_UPDATE_FAILED,
                    'errors': ve.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return Response(
                {
                    'detail': ERROR_PRODUCT_UPDATE_FAILED,
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a product"""
        product = self.get_object()
        
        try:
            # Use ProductService directly for deletion
            ProductService.delete_product(product, request.user)
            return Response(
                {'detail': SUCCESS_PRODUCT_DELETED},
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
        except Exception as e:
            logger.error(f"Error deleting product: {str(e)}")
            return Response(
                {'detail': ERROR_PRODUCT_DELETE_FAILED},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='my-products')
    def my_products(self, request):
        """
        Get products belonging to the authenticated user's brand
        GET /api/products/my-products/
        """
        if not hasattr(request.user, 'userprofile') or not hasattr(request.user.userprofile, 'brandprofile'):
            return Response(
                {'detail': "User does not have a brand profile"},
                status=status.HTTP_400_BAD_REQUEST
            )

        products = self.get_queryset().filter(brand=request.user.userprofile.brandprofile)
        
        # Apply filtering
        products = self.filter_queryset(products)
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='similar')
    def similar_products(self, request, slug=None):
        """
        Get similar products based on category and characteristics
        GET /api/products/{slug}/similar/
        """
        product = self.get_object()
        
        # Find similar products (same category, similar characteristics)
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(
            id=product.id
        ).filter(
            Q(base_type=product.base_type) |
            Q(packaging_material=product.packaging_material)
        ).select_related('category', 'brand')[:8]  # Removed prefetch_related('images')
        
        serializer = ProductListSerializer(
            similar_products, 
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='remove-image')
    def remove_image(self, request, slug=None):
        """
        Custom action to remove product image
        DELETE /api/products/{slug}/remove-image/
        """
        product = self.get_object()
        
        # Check if product belongs to user's brand
        if not hasattr(request.user, 'userprofile') or not hasattr(request.user.userprofile, 'brandprofile') or product.brand.id != request.user.userprofile.brandprofile.id:
            return Response(
                {'detail': ERROR_PRODUCT_BRAND_MISMATCH},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Verificar si tiene imagen
            if not product.image:
                return Response(
                    {'detail': "Product does not have an image"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Eliminar la imagen
            product.image.delete(save=False)
            product.image = None
            product.save()
            
            return Response(
                {'detail': SUCCESS_PRODUCT_IMAGE_REMOVED},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error removing product image: {str(e)}")
            return Response(
                {'detail': ERROR_PRODUCT_IMAGE_UPLOAD_FAILED},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['put'], url_path='upload-image', 
            parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, slug=None):
        """
        Custom action to upload/update product image
        PUT/PATCH /api/products/{slug}/upload-image/
        
        Expected form data: {'image': <file>}
        """
        product = self.get_object()
        
        # Check if product belongs to user's brand
        if not hasattr(request.user, 'userprofile') or not hasattr(request.user.userprofile, 'brandprofile') or product.brand.id != request.user.userprofile.brandprofile.id:
            return Response(
                {'detail': ERROR_PRODUCT_BRAND_MISMATCH},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Usar el ProductImageFieldSerializer para validar la imagen
        serializer = ProductImageFieldSerializer(
            product, 
            data=request.data,
            context={'request': request},
            partial=True
        )
        
        if serializer.is_valid():
            # Actualizar solo la imagen
            if 'image' in serializer.validated_data:
                # Borrar imagen anterior si existe
                if product.image:
                    product.image.delete(save=False)
                
                product.image = serializer.validated_data['image']
                product.save()
            
            return Response(
                {
                    'detail': SUCCESS_PRODUCT_IMAGE_UPLOADED,
                    'image_url': serializer.data.get('image_url')
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {
                'detail': ERROR_PRODUCT_IMAGE_UPLOAD_FAILED,
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )