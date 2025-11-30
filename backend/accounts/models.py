"""
Description: User Profile and Brand Profile Models
 
File: models.py
Author: Anthony Bañon
Created: 2025-11-29
Last Updated: 2025-11-29
"""


from django.contrib.auth.models import User
from django.db import models
from .constants import *


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=MAX_PHONE_LENGTH, blank=True)
    eco_points = models.IntegerField(default=MIN_ECO_POINTS)
    total_carbon_saved = models.FloatField(default=MIN_CARBON_SAVED)  # kg CO2
    is_brand_manager = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} Profile"

class BrandProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=MAX_BRAND_NAME_LENGTH)
    sustainability_story = models.TextField(blank=True)
    
    def __str__(self):
        return self.brand_name
