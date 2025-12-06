"""
Rewards URLs

File: urls.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create routers
points_router = DefaultRouter()
points_router.register(r'points', views.PointsViewSet, basename='points')

rewards_router = DefaultRouter()
rewards_router.register(r'rewards', views.RewardsViewSet, basename='user-rewards')

admin_router = DefaultRouter()
admin_router.register(r'admin/rewards', views.AdminRewardsViewSet, basename='admin-rewards')

# URL patterns
urlpatterns = [
    # User points routes
    path('', include(points_router.urls)),
    
    # User points custom endpoints
    # GET    /api/points/                    # List user transactions
    # POST   /api/points/earn/              # Earn points
    # GET    /api/points/summary/           # Get points summary
    
    # User rewards routes
    path('', include(rewards_router.urls)),
    
    # User rewards custom endpoints
    # GET    /api/rewards/                   # List available rewards
    # POST   /api/rewards/claim/            # Claim a reward
    
    # Public rewards (no authentication)
    path('rewards/public/', views.PublicRewardsView.as_view(), name='public-rewards'),
    
    # Admin routes
    path('', include(admin_router.urls)),
    
    # Admin custom endpoints
    # GET    /api/admin/rewards/                    # List all rewards
    # POST   /api/admin/rewards/create_reward/      # Create reward
    # PUT    /api/admin/rewards/update_reward/      # Update reward (with ?reward_id=)
    # DELETE /api/admin/rewards/delete_reward/      # Delete reward (with ?reward_id=)
    # GET    /api/admin/rewards/leaderboard/        # Get points leaderboard
    # GET    /api/admin/rewards/statistics/         # Get rewards statistics
]