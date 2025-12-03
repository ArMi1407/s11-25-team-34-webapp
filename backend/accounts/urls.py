from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para ViewSets
router = DefaultRouter()
router.register(r'profile', views.UserProfileViewSet, basename='userprofile')

urlpatterns = [
    # Authentication
    path('auth/login/', views.LoginUserView.as_view(), name='login'),
    path('auth/logout/', views.LogoutUserView.as_view(), name='logout'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # User Registration
    path('auth/register/', views.RegisterUserView.as_view(), name='register'),
    
    # Brand Registration & Operations
    path('brand/register/', views.RegisterBrandManagerView.as_view(), name='register-brand'),
    path('brand/profile/', views.BrandProfileView.as_view(), name='brand-profile'),
    path('brand/story/', views.UpdateBrandStoryView.as_view(), name='update-brand-story'),
    path('brand/delete/', views.DeleteBrandProfileView.as_view(), name='delete-brand-profile'),
    
    # Include router URLs (UserProfileViewSet)
    path('', include(router.urls)),
]