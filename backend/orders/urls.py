"""
Orders URLs

File: urls.py
Author: Anthony Bañon
Created: 2025-12-05
Last Updated: 2025-12-05
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create routers
user_router = DefaultRouter()
user_router.register(r'orders', views.OrderViewSet, basename='user-order')

admin_router = DefaultRouter()
admin_router.register(r'admin/orders', views.AdminOrderViewSet, basename='admin-order')

# URL patterns
urlpatterns = [
    # User order routes
    path('', include(user_router.urls)),
    
    # User order custom endpoints
    # GET    /api/orders/                    # List user orders
    # GET    /api/orders/{id}/              # Get order details
    # POST   /api/orders/{id}/cancel/       # Cancel order
    # GET    /api/orders/{id}/status_history/  # Get status history
    # GET    /api/orders/{id}/payment_info/   # Get payment info
    
    # Payment endpoints
    path('orders/<int:order_id>/payments/', 
         views.CreatePaymentView.as_view(), 
         name='create-payment'),
    
    path('payments/<int:payment_id>/webhook/', 
         views.PaymentWebhookView.as_view(), 
         name='payment-webhook'),
    
    # Admin routes
    path('', include(admin_router.urls)),
    
    # Admin custom endpoints
    # GET    /api/admin/orders/                    # List all orders with filters
    # PUT    /api/admin/orders/{id}/update_status/  # Update order status
    # GET    /api/admin/orders/statistics/         # Get statistics
]