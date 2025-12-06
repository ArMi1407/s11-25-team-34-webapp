# rewards/models.py
from django.db import models
from orders.models import Order
from .constants import *

class EcoTransaction(models.Model):
    ACTION_TYPES = ACTION_TYPE_CHOICES
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    points_earned = models.IntegerField()
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    carbon_saved = models.FloatField(default=0.0)  # kg CO2 ahorrado
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.points_earned} points for {self.user.username}"

class EcoReward(models.Model):
    REWARD_TYPES = REWARD_TYPE_CHOICES
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['points_required']
    
    def __str__(self):
        return self.name