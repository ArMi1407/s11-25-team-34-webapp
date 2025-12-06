"""
Rewards Service layer ONLY for complex business logic

File: services.py  
Author: [Tu Nombre]
Created: 2025-12-01
"""

from django.db import transaction, models
from accounts.models import UserProfile
from django.utils import timezone
from .models import EcoTransaction, EcoReward
from orders.models import Order
from .constants import *
from datetime import timedelta



class BusinessException(Exception):
    """Custom exception for business logic errors"""
    pass


class PointsService:
    """
    Service ONLY for complex points operations
    """
    
    def _calculate_purchase_points(self, order):
        """
        Calculate points based on order total
        """
        points = int(order.total_amount * POINTS_PER_DOLLAR)
        carbon_saved = order.total_carbon_footprint * 0.1  # Assume 10% carbon saved
        
        return points, carbon_saved
    
    def _get_action_points(self, action_type):
        """
        Get fixed points for specific actions
        """
        points_map = {
            ACTION_REVIEW: POINTS_FOR_REVIEW,
            ACTION_REFERRAL: POINTS_FOR_REFERRAL,
            ACTION_LOGIN_STREAK: POINTS_FOR_LOGIN_STREAK,
        }
        
        return points_map.get(action_type, 0)
    
    @transaction.atomic
    def earn_points(self, user, action_type, order_id=None, custom_points=None, custom_carbon_saved=0.0):
        """
        Complex operation: Earn points with business rules
        ASSUMES data already validated by serializer
        """
        points = 0
        carbon_saved = 0.0
        
        # Calculate points based on action type
        if action_type == ACTION_PURCHASE:
            if not order_id:
                raise BusinessException("Order ID required for purchase action")
            
            try:
                order = Order.objects.get(id=order_id, user=user)
                
                # Check if points already awarded for this order
                if EcoTransaction.objects.filter(user=user, order=order, action_type=ACTION_PURCHASE).exists():
                    raise BusinessException("Points already awarded for this order")
                
                points, carbon_saved = self._calculate_purchase_points(order)
                
            except Order.DoesNotExist:
                raise BusinessException("Order not found or does not belong to user")
        
        elif action_type in [ACTION_REVIEW, ACTION_REFERRAL, ACTION_LOGIN_STREAK]:
            points = self._get_action_points(action_type)
            carbon_saved = points * 0.01  # 0.01 kg CO2 per point
        
        else:
            # Custom action with manual points
            if custom_points is None:
                raise BusinessException("Points required for custom action")
            
            points = custom_points
            carbon_saved = custom_carbon_saved or (points * 0.01)
        
        # Validate points limits
        if points > MAX_POINTS_PER_TRANSACTION:
            raise BusinessException(f"Cannot award more than {MAX_POINTS_PER_TRANSACTION} points per transaction")
        
        if carbon_saved > MAX_CARBON_SAVED_PER_TRANSACTION:
            raise BusinessException(f"Carbon saved cannot exceed {MAX_CARBON_SAVED_PER_TRANSACTION} kg")
        
        # Create transaction
        eco_transaction = EcoTransaction.objects.create(
            user=user,
            order_id=order_id if action_type == ACTION_PURCHASE else None,
            points_earned=points,
            action_type=action_type,
            carbon_saved=carbon_saved
        )
        
        # Update user profile
        
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.eco_points += points
        user_profile.total_carbon_saved += carbon_saved
        user_profile.save()
        
        return eco_transaction
    
    def get_user_transactions(self, user, limit=50):
        """
        Get user's eco transactions
        """
        return EcoTransaction.objects.filter(user=user).order_by('-created_at')[:limit]
    
    def get_user_points_summary(self, user):
        """
        Get comprehensive points summary for user
        """

        
        try:
            user_profile = UserProfile.objects.get(user=user)
            
            # Get recent transactions
            recent_transactions = self.get_user_transactions(user, limit=10)
            
            # Get available rewards
            available_rewards = EcoReward.objects.filter(
                is_active=True,
                points_required__lte=user_profile.eco_points
            ).order_by('points_required')
            
            return {
                'total_points': user_profile.eco_points,
                'total_carbon_saved': user_profile.total_carbon_saved,
                'recent_transactions': recent_transactions,
                'available_rewards': available_rewards
            }
            
        except UserProfile.DoesNotExist:
            return {
                'total_points': 0,
                'total_carbon_saved': 0.0,
                'recent_transactions': [],
                'available_rewards': []
            }


class RewardsService:
    """
    Service ONLY for complex rewards operations
    """
    
    @transaction.atomic
    def claim_reward(self, user, reward_id):
        """
        Complex operation: Claim reward with business rules
        ASSUMES data already validated by serializer
        """
        try:
            reward = EcoReward.objects.get(id=reward_id, is_active=True)
        except EcoReward.DoesNotExist:
            raise BusinessException(ERROR_REWARD_NOT_ACTIVE)
        
        # Check user points

        
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        
        if user_profile.eco_points < reward.points_required:
            raise BusinessException(ERROR_INSUFFICIENT_POINTS)
        
        # Deduct points
        user_profile.eco_points -= reward.points_required
        user_profile.save()
        
        # Create transaction record
        EcoTransaction.objects.create(
            user=user,
            points_earned=-reward.points_required,  # Negative for redemption
            action_type=ACTION_REWARD_CLAIM,
            carbon_saved=0.0
        )
        
        # Generate reward code based on type
        reward_code = self._generate_reward_code(reward, user)
        
        return {
            'reward': reward,
            'reward_code': reward_code,
            'remaining_points': user_profile.eco_points
        }
    
    def _generate_reward_code(self, reward, user):
        """
        Generate reward code based on reward type
        """
        import uuid
        
        prefix_map = {
            REWARD_DISCOUNT: 'DISC',
            REWARD_DONATION: 'DONA',
            REWARD_PRODUCT: 'PROD',
        }
        
        prefix = prefix_map.get(reward.reward_type, 'REWD')
        code = f"{prefix}-{user.id}-{uuid.uuid4().hex[:8].upper()}"
        
        # In real implementation, you would save this to a RewardRedemption model
        return code
    
    @transaction.atomic
    def create_reward(self, reward_data):
        """
        Create new reward
        ASSUMES data already validated by serializer
        """
        reward = EcoReward.objects.create(**reward_data)
        return reward
    
    @transaction.atomic
    def update_reward(self, reward_id, update_data):
        """
        Update existing reward
        """
        try:
            reward = EcoReward.objects.get(id=reward_id)
        except EcoReward.DoesNotExist:
            raise BusinessException(ERROR_REWARD_NOT_FOUND)
        
        for field, value in update_data.items():
            setattr(reward, field, value)
        
        reward.save()
        return reward
    
    @transaction.atomic
    def delete_reward(self, reward_id):
        """
        Delete reward (soft delete by deactivating)
        """
        try:
            reward = EcoReward.objects.get(id=reward_id)
        except EcoReward.DoesNotExist:
            raise BusinessException(ERROR_REWARD_NOT_FOUND)
        
        reward.is_active = False
        reward.save()
        
        return True
    
    def get_available_rewards(self, user=None):
        """
        Get all active rewards, optionally filtered by user points
        """
        queryset = EcoReward.objects.filter(is_active=True).order_by('points_required')
        
        if user:
            
            try:
                user_profile = UserProfile.objects.get(user=user)
                # Filter rewards user can afford
                queryset = queryset.filter(points_required__lte=user_profile.eco_points)
            except UserProfile.DoesNotExist:
                pass
        
        return queryset


class AdminRewardsService:
    """
    Service ONLY for admin rewards operations
    """
    
    def get_points_leaderboard(self, limit=50, timeframe_days=None):
        """
        Get points leaderboard
        """       
        queryset = UserProfile.objects.all()
        
        if timeframe_days:
            date_from = timezone.now() - timedelta(days=timeframe_days)
            # This would require a date field in EcoTransaction or UserProfile
            # For simplicity, we're not filtering by timeframe here
        
        leaderboard = []
        for profile in queryset.order_by('-eco_points')[:limit]:
            leaderboard.append({
                'user_id': profile.user.id,
                'username': profile.user.username,
                'total_points': profile.eco_points,
                'total_carbon_saved': profile.total_carbon_saved,
                'is_brand_manager': profile.is_brand_manager
            })
        
        return leaderboard
    
    def get_rewards_statistics(self):
        """
        Get rewards statistics
        """
        total_rewards = EcoReward.objects.count()
        active_rewards = EcoReward.objects.filter(is_active=True).count()
        
        # Count by type
        rewards_by_type = EcoReward.objects.values('reward_type').annotate(
            count=models.Count('id'),
            avg_points=models.Avg('points_required')
        )
        
        # Most popular rewards (would need redemption tracking)
        # For now, just return basic stats
        
        return {
            'total_rewards': total_rewards,
            'active_rewards': active_rewards,
            'rewards_by_type': list(rewards_by_type)
        }