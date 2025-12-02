"""
Application Constants

File: constants.py
Author: Anthony Bañon
Created: 2025-11-29
Last Updated: 2025-11-29
"""

# Eco Points Business Rules
MAX_ECO_POINTS_ADDITION = 10000
MAX_CARBON_SAVED_ADDITION = 1000.0
MIN_ECO_POINTS = 0
MIN_CARBON_SAVED = 0.0

# Brand Profile Business Rules
MAX_SUSTAINABILITY_STORY_LENGTH = 5000
MAX_BRAND_NAME_LENGTH = 100

# User Profile Business Rules
MAX_NAME_LENGTH = 50
MAX_PHONE_LENGTH = 20
DEFAULT_ECO_POINTS = 0
DEFAULT_CARBON_SAVED = 0.0

# Validation Messages
VALIDATION_USERNAME_REQUIRED = "Username is required"
VALIDATION_EMAIL_REQUIRED = "Email is required"
VALIDATION_PASSWORD_MISMATCH = "Passwords do not match"
VALIDATION_BRAND_NAME_REQUIRED = "Brand name is required"
VALIDATION_STORY_REQUIRED = "Sustainability story is required"

# Error Messages
ERROR_USER_NOT_FOUND = "User not found"
ERROR_PROFILE_NOT_FOUND = "User profile not found"
ERROR_BRAND_NOT_FOUND = "Brand profile not found"
ERROR_NOT_BRAND_MANAGER = "User is not a brand manager"
ERROR_BRAND_NAME_EXISTS = "Brand name already exists"
ERROR_USERNAME_EXISTS = "Username already registered"
ERROR_EMAIL_EXISTS = "Email already registered"
ERROR_INVALID_CREDENTIALS = "Invalid username or password"
ERROR_ACCOUNT_DEACTIVATED = "Account is deactivated"
ERROR_POINTS_EXCEED_LIMIT = "Points amount exceeds maximum allowed"
ERROR_CARBON_EXCEED_LIMIT = "Carbon saved amount exceeds maximum allowed"
ERROR_STORY_EXCEED_LENGTH = "Sustainability story exceeds maximum length"

# Success Messages
SUCCESS_REGISTRATION = "User registered successfully"
SUCCESS_LOGIN = "Login successful"
SUCCESS_LOGOUT = "Logout successful"
SUCCESS_PROFILE_UPDATED = "Profile updated successfully"
SUCCESS_ECO_POINTS_ADDED = "Eco points added successfully"
SUCCESS_BRAND_STORY_UPDATED = "Brand story updated successfully"
SUCCESS_PASSWORD_CHANGED = "Changed password successfully"

