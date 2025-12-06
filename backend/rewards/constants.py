"""
Rewards Constants

File: constants.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

# Transaction action types
ACTION_PURCHASE = 'purchase'
ACTION_REVIEW = 'review'
ACTION_REFERRAL = 'referral'
ACTION_LOGIN_STREAK = 'login_streak'
ACTION_REWARD_CLAIM = 'reward_claim'

ACTION_TYPE_CHOICES = [
    (ACTION_PURCHASE, 'Purchase'),
    (ACTION_REVIEW, 'Review'),
    (ACTION_REFERRAL, 'Referral'),
    (ACTION_LOGIN_STREAK, 'Login Streak'),
    (ACTION_REWARD_CLAIM, 'Reward Claim'),
]

# Reward types
REWARD_DISCOUNT = 'discount'
REWARD_DONATION = 'donation'
REWARD_PRODUCT = 'product'

REWARD_TYPE_CHOICES = [
    (REWARD_DISCOUNT, 'Discount Coupon'),
    (REWARD_DONATION, 'Environmental Donation'),
    (REWARD_PRODUCT, 'Free Product'),
]

# Points configuration
POINTS_PER_DOLLAR = 10  # Points earned per dollar spent
POINTS_FOR_REVIEW = 50
POINTS_FOR_REFERRAL = 500
POINTS_FOR_LOGIN_STREAK = 100

# Limits
MAX_POINTS_PER_TRANSACTION = 10000
MAX_CARBON_SAVED_PER_TRANSACTION = 100.0

# Error messages
ERROR_INSUFFICIENT_POINTS = "Insufficient eco points for this reward"
ERROR_REWARD_NOT_ACTIVE = "This reward is no longer available"
ERROR_REWARD_NOT_FOUND = "Reward not found"
ERROR_INVALID_ACTION = "Invalid action type"
ERROR_TRANSACTION_NOT_FOUND = "Transaction not found"

# Success messages
SUCCESS_POINTS_EARNED = "Points earned successfully"
SUCCESS_REWARD_CLAIMED = "Reward claimed successfully"
SUCCESS_REWARD_CREATED = "Reward created successfully"
SUCCESS_REWARD_UPDATED = "Reward updated successfully"
SUCCESS_REWARD_DELETED = "Reward deleted successfully"