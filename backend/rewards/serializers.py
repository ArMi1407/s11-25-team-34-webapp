"""
Rewards Serializers ONLY for validation and formatting

File: serializers.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EcoTransaction, EcoReward
from orders.models import Order
from .constants import *


##### EcoTransaction Serializers #####

class EcoTransactionSerializer(serializers.ModelSerializer):
    """Formatting ONLY for eco transaction output"""
    username = serializers.CharField(source='user.username', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True, allow_null=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    
    class Meta:
        model = EcoTransaction
        fields = [
            'id', 'user', 'username', 'order', 'order_number', 
            'points_earned', 'action_type', 'action_type_display',
            'carbon_saved', 'created_at'
        ]
        read_only_fields = fields


class PointsEarnSerializer(serializers.Serializer):
    """Validation ONLY for earning points"""
    action_type = serializers.ChoiceField(choices=ACTION_TYPE_CHOICES, required=True)
    order_id = serializers.IntegerField(required=False, allow_null=True)
    points = serializers.IntegerField(required=False, min_value=1, max_value=MAX_POINTS_PER_TRANSACTION)
    carbon_saved = serializers.FloatField(required=False, min_value=0.0, max_value=MAX_CARBON_SAVED_PER_TRANSACTION)
    
    def validate(self, attrs):
        action_type = attrs.get('action_type')
        
        # Validate order_id for purchase actions
        if action_type == ACTION_PURCHASE and not attrs.get('order_id'):
            raise serializers.ValidationError({
                "order_id": "Order ID is required for purchase actions"
            })
        
        # Validate points/carbon_saved for manual entries
        if action_type not in [ACTION_PURCHASE, ACTION_REVIEW, ACTION_REFERRAL, ACTION_LOGIN_STREAK]:
            if not attrs.get('points'):
                raise serializers.ValidationError({
                    "points": "Points are required for custom actions"
                })
        
        return attrs
    
    def validate_order_id(self, value):
        if value:
            try:
                Order.objects.get(id=value)
            except Order.DoesNotExist:
                raise serializers.ValidationError("Order not found")
        return value


##### EcoReward Serializers #####

class EcoRewardSerializer(serializers.ModelSerializer):
    """Formatting ONLY for eco reward output"""
    reward_type_display = serializers.CharField(source='get_reward_type_display', read_only=True)
    
    class Meta:
        model = EcoReward
        fields = [
            'id', 'name', 'description', 'points_required', 
            'reward_type', 'reward_type_display', 'is_active'
        ]
        read_only_fields = fields


class EcoRewardCreateSerializer(serializers.Serializer):
    """Validation ONLY for reward creation"""
    name = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(required=True)
    points_required = serializers.IntegerField(required=True, min_value=1)
    reward_type = serializers.ChoiceField(choices=REWARD_TYPE_CHOICES, required=True)
    is_active = serializers.BooleanField(default=True, required=False)
    
    def validate_points_required(self, value):
        if value > 100000:
            raise serializers.ValidationError("Points required cannot exceed 100,000")
        return value


class EcoRewardUpdateSerializer(serializers.Serializer):
    """Validation ONLY for reward update"""
    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False)
    points_required = serializers.IntegerField(required=False, min_value=1)
    is_active = serializers.BooleanField(required=False)


class ClaimRewardSerializer(serializers.Serializer):
    """Validation ONLY for claiming rewards"""
    reward_id = serializers.IntegerField(required=True)
    
    def validate_reward_id(self, value):
        try:
            EcoReward.objects.get(id=value)
        except EcoReward.DoesNotExist:
            raise serializers.ValidationError(ERROR_REWARD_NOT_FOUND)
        return value


##### User Points Serializers #####

class UserPointsSummarySerializer(serializers.Serializer):
    """Formatting ONLY for user points summary"""
    total_points = serializers.IntegerField()
    total_carbon_saved = serializers.FloatField()
    recent_transactions = EcoTransactionSerializer(many=True)
    available_rewards = EcoRewardSerializer(many=True)