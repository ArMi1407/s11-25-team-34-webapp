"""
Rewards Views - Use appropriate view type for each case

File: views.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

from rest_framework import generics, viewsets, status, mixins
from rest_framework.views import APIView
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction

from .models import EcoTransaction, EcoReward
from .serializers import *
from .services import PointsService, RewardsService, AdminRewardsService, BusinessException
from .constants import *


##### User Points Views (ViewSet for user points operations) #####

class PointsViewSet(viewsets.ViewSet):
    """✅ ViewSet for user points operations"""
    permission_classes = [IsAuthenticated]
    
    def _get_points_service(self):
        return PointsService()
    
    # Swagger documentation workaround
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return EcoTransaction.objects.none()
        return EcoTransaction.objects.all()
    
    def list(self, request):
        """✅ Get user's eco transactions"""
        points_service = self._get_points_service()
        transactions = points_service.get_user_transactions(request.user)
        serializer = EcoTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def earn(self, request):
        """✅ Earn points for specific actions (complex logic in service)"""
        serializer = PointsEarnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        points_service = self._get_points_service()
        
        try:
            processing = points_service.earn_points(
                user=request.user,
                action_type=serializer.validated_data['action_type'],
                order_id=serializer.validated_data.get('order_id'),
                custom_points=serializer.validated_data.get('points'),
                custom_carbon_saved=serializer.validated_data.get('carbon_saved', 0.0)
            )
            
            return Response({
                'message': SUCCESS_POINTS_EARNED,
                'data': {
                    'transaction': EcoTransactionSerializer(processing).data,
                    'points_earned': processing.points_earned,
                    'carbon_saved': processing.carbon_saved,
                    'action_type': processing.action_type
                }
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """✅ Get user points summary"""
        points_service = self._get_points_service()
        
        try:
            summary = points_service.get_user_points_summary(request.user)
            
            return Response({
                'message': 'Points summary retrieved successfully',
                'data': summary
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


##### Rewards Views (ViewSet for rewards operations) #####

class RewardsViewSet(viewsets.ViewSet):
    """✅ ViewSet for rewards operations"""
    permission_classes = [IsAuthenticated]
    
    def _get_rewards_service(self):
        return RewardsService()
    
    # Swagger documentation workaround
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return EcoReward.objects.none()
        return EcoReward.objects.all()
    
    def list(self, request):
        """✅ Get available rewards for user"""
        rewards_service = self._get_rewards_service()
        rewards = rewards_service.get_available_rewards(request.user)
        serializer = EcoRewardSerializer(rewards, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def claim(self, request):
        """✅ Claim a reward (complex logic in service)"""
        serializer = ClaimRewardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rewards_service = self._get_rewards_service()
        
        try:
            result = rewards_service.claim_reward(
                user=request.user,
                reward_id=serializer.validated_data['reward_id']
            )
            
            return Response({
                'message': SUCCESS_REWARD_CLAIMED,
                'data': {
                    'reward': EcoRewardSerializer(result['reward']).data,
                    'reward_code': result['reward_code'],
                    'remaining_points': result['remaining_points']
                }
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


##### Admin Rewards Views (for staff users) #####

class AdminRewardsViewSet(viewsets.ViewSet):
    """✅ ViewSet for admin rewards management"""
    permission_classes = [IsAdminUser]
    
    def _get_rewards_service(self):
        return RewardsService()
    
    def _get_admin_service(self):
        return AdminRewardsService()
    
    def list(self, request):
        """✅ Get all rewards (admin view)"""
        rewards_service = self._get_rewards_service()
        rewards = EcoReward.objects.all().order_by('-id')
        serializer = EcoRewardSerializer(rewards, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def create_reward(self, request):
        """✅ Create new reward (admin only)"""
        serializer = EcoRewardCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rewards_service = self._get_rewards_service()
        
        try:
            reward = rewards_service.create_reward(serializer.validated_data)
            
            return Response({
                'message': SUCCESS_REWARD_CREATED,
                'data': EcoRewardSerializer(reward).data
            }, status=status.HTTP_201_CREATED)
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'])
    @transaction.atomic
    def update_reward(self, request):
        """✅ Update reward (admin only)"""
        reward_id = request.query_params.get('reward_id')
        if not reward_id:
            return Response({'error': 'reward_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = EcoRewardUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        rewards_service = self._get_rewards_service()
        
        try:
            reward = rewards_service.update_reward(
                reward_id,
                serializer.validated_data
            )
            
            return Response({
                'message': SUCCESS_REWARD_UPDATED,
                'data': EcoRewardSerializer(reward).data
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    @transaction.atomic
    def delete_reward(self, request):
        """✅ Delete reward (admin only - soft delete)"""
        reward_id = request.query_params.get('reward_id')
        if not reward_id:
            return Response({'error': 'reward_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        rewards_service = self._get_rewards_service()
        
        try:
            rewards_service.delete_reward(reward_id)
            
            return Response({
                'message': SUCCESS_REWARD_DELETED,
                'data': None
            })
            
        except BusinessException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """✅ Get points leaderboard (admin only)"""
        admin_service = self._get_admin_service()
        
        limit = int(request.query_params.get('limit', 50))
        timeframe = request.query_params.get('timeframe')
        timeframe_days = int(timeframe) if timeframe else None
        
        leaderboard = admin_service.get_points_leaderboard(limit, timeframe_days)
        
        return Response({
            'message': 'Leaderboard retrieved successfully',
            'data': {
                'leaderboard': leaderboard,
                'total_users': len(leaderboard)
            }
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """✅ Get rewards statistics (admin only)"""
        admin_service = self._get_admin_service()
        
        statistics = admin_service.get_rewards_statistics()
        
        return Response({
            'message': 'Statistics retrieved successfully',
            'data': statistics
        })


##### Public Rewards Views (for all users) #####

class PublicRewardsView(generics.ListAPIView):
    """✅ ListAPIView for public rewards (no authentication required)"""
    permission_classes = [AllowAny]
    serializer_class = EcoRewardSerializer
    
    def get_queryset(self):
        return EcoReward.objects.filter(is_active=True).order_by('points_required')