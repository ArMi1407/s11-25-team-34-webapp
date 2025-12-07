"""
Cart URLs

File: urls.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSet endpoints
router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart/items', views.CartItemViewSet, basename='cart-items')

# URL patterns
urlpatterns = [
    # Cart ViewSet routes (automatic routing for list/create/retrieve/update/destroy)
    path('', include(router.urls)),
    
    # Custom endpoints for ViewSet actions
    # Note: These are already included by the router, but we list them here for clarity
    # POST   /api/cart/add_item/
    # PUT    /api/cart/update_item/
    # DELETE /api/cart/remove_item/
    # DELETE /api/cart/clear/
    
    # Additional standalone endpoints
    path('checkout/', views.CheckoutView.as_view(), name='cart-checkout'),
    path('merge/', views.MergeCartView.as_view(), name='cart-merge'),
]