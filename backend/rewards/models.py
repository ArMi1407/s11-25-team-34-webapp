# rewards/models.py
from django.db import models
from orders.models import Order

class EcoTransaction(models.Model):
    ACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('review', 'Review'),
        ('referral', 'Referral'),
        ('login_streak', 'Login Streak')
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    points_earned = models.IntegerField()
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    carbon_saved = models.FloatField(default=0.0)  # kg CO2 ahorrado
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.points_earned} points for {self.user.username}"

class EcoReward(models.Model):
    REWARD_TYPES = [
        ('discount', 'Discount Coupon'),
        ('donation', 'Environmental Donation'),
        ('product', 'Free Product')
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name