"""
Description: Category Urls
 
File: urls.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    
    # Additional product endpoints
    
    # Nested routes (optional - if you want category-specific products)
    path('categories/<slug:slug>/products/', 
         ProductViewSet.as_view({'get': 'list'}), 
         name='category-products'),
]