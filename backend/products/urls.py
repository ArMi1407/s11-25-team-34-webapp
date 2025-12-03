"""
Description: Category Urls
 
File: urls.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]