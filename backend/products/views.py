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

from rest_framework import viewsets, status, filters, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Category, Product
from .serializers import CategorySerializer, CategoryListSerializer, CategoryImageSerializer, ProductSerializer, ProductListSerializer, ProductCreateSerializer
from .services import CategoryService, ProductService, BusinessException
from .constants import *
from .filters import ProductFilter

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
        if self.request.user.is_authenticated and hasattr(self.request.user, 'brandprofile'):
            if self.action in ['my_products', 'update', 'partial_update', 'destroy']:
                # For specific actions, include inactive products for brand owners
                queryset = queryset.filter(brand=self.request.user.brandprofile)
            elif self.action == 'list':
                # In list view, brand owners see their inactive products too
                if self.request.query_params.get('my_products') == 'true':
                    queryset = queryset.filter(brand=self.request.user.brandprofile)
        
        # Optimize queries
        if self.action == 'list':
            queryset = queryset.select_related('category', 'brand').prefetch_related('images')
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializer based on action"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        """
        Override permissions for specific actions
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 
                          'activate', 'deactivate', 'my_products']:
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
            self.perform_create(serializer)
            return Response(
                {
                    'detail': SUCCESS_PRODUCT_CREATED,
                    'product': serializer.data
                },
                status=status.HTTP_201_CREATED
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
        if not hasattr(request.user, 'brandprofile') or product.brand != request.user.brandprofile:
            return Response(
                {'detail': ERROR_PRODUCT_BRAND_MISMATCH},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(product, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_update(serializer)
            return Response(
                {
                    'detail': SUCCESS_PRODUCT_UPDATED,
                    'product': serializer.data
                },
                status=status.HTTP_200_OK
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
    
    @action(detail=False, methods=['get'], url_path='my-products')
    def my_products(self, request):
        """
        Get products belonging to the authenticated user's brand
        GET /api/products/my-products/
        """
        if not hasattr(request.user, 'brandprofile'):
            return Response(
                {'detail': "User does not have a brand profile"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = self.get_queryset().filter(brand=request.user.brandprofile)
        
        # Apply filtering
        products = self.filter_queryset(products)
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, slug=None):
        """
        Activate a product
        POST /api/products/{slug}/activate/
        """
        product = self.get_object()
        
        try:
            ProductService.toggle_product_active(product, request.user, activate=True)
            return Response(
                {'detail': SUCCESS_PRODUCT_ACTIVATED},
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
    
    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, slug=None):
        """
        Deactivate a product
        POST /api/products/{slug}/deactivate/
        """
        product = self.get_object()
        
        try:
            ProductService.toggle_product_active(product, request.user, activate=False)
            return Response(
                {'detail': SUCCESS_PRODUCT_DEACTIVATED},
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
    
    @action(detail=True, methods=['get'], url_path='similar')
    def similar_products(self, request, slug=None):
        """
        Get similar products based on category and characteristics
        GET /api/products/{slug}/similar/
        """
        product = self.get_object()
        
        # Find similar products (same category, similar price range)
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(
            id=product.id
        ).filter(
            Q(base_type=product.base_type) |
            Q(packaging_material=product.packaging_material)
        ).select_related('category', 'brand').prefetch_related('images')[:8]
        
        serializer = ProductListSerializer(
            similar_products, 
            many=True,
            context={'request': request}
        )
        
        return Response(serializer.data)

class ProductSearchView(generics.ListAPIView):
    """
    Dedicated search view for products with advanced filtering
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'ingredient_main', 'brand__name']
    ordering_fields = ['price', 'carbon_footprint', 'created_at']
    
    def get_queryset(self):
        """Optimize search queryset"""
        queryset = super().get_queryset()
        queryset = queryset.select_related('category', 'brand').prefetch_related('images')
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override to add search metadata"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get search query
        search_query = request.query_params.get('search', '')
        
        # Validate search query length
        if search_query and len(search_query) < PRODUCT_SEARCH_MIN_QUERY_LENGTH:
            return Response(
                {
                    'detail': f"Search query must be at least {PRODUCT_SEARCH_MIN_QUERY_LENGTH} characters"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['search_query'] = search_query
            response.data['total_results'] = queryset.count()
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'search_query': search_query,
            'total_results': queryset.count()
        })