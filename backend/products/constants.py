"""
Application Constants for Category and Product

File: constants.py
Author: Anthony Bañon
Created: 2025-12-03
Last Updated: 2025-12-03
"""

# =============================================================================
# CATEGORY CONSTANTS
# =============================================================================

# Category Business Rules
CATEGORY_NAME_MIN_LENGTH = 2
CATEGORY_NAME_MAX_LENGTH = 100
CATEGORY_DESCRIPTION_MAX_LENGTH = 5000
CATEGORY_SLUG_MAX_LENGTH = 50

# Category Validation Messages
VALIDATION_CATEGORY_NAME_REQUIRED = "Category name is required"
VALIDATION_CATEGORY_NAME_TOO_SHORT = f"Category name must be at least {CATEGORY_NAME_MIN_LENGTH} characters long"
VALIDATION_CATEGORY_NAME_TOO_LONG = f"Category name cannot exceed {CATEGORY_NAME_MAX_LENGTH} characters"
VALIDATION_CATEGORY_SLUG_REQUIRED = "Category slug is required"
VALIDATION_CATEGORY_SLUG_EXISTS = "A category with this slug already exists"
VALIDATION_CATEGORY_DESCRIPTION_TOO_LONG = f"Category description cannot exceed {CATEGORY_DESCRIPTION_MAX_LENGTH} characters"

# Category Image Business Rules
CATEGORY_IMAGE_MAX_SIZE_MB = 5
CATEGORY_IMAGE_MAX_SIZE_BYTES = CATEGORY_IMAGE_MAX_SIZE_MB * 1024 * 1024
CATEGORY_IMAGE_ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
CATEGORY_IMAGE_ALLOWED_FORMATS_STR = ', '.join(CATEGORY_IMAGE_ALLOWED_EXTENSIONS).replace('.', '')

# Category Image Validation Messages
VALIDATION_CATEGORY_IMAGE_TOO_LARGE = f"Category image size cannot exceed {CATEGORY_IMAGE_MAX_SIZE_MB}MB"
VALIDATION_CATEGORY_IMAGE_INVALID_FORMAT = f"Unsupported image format. Allowed formats: {CATEGORY_IMAGE_ALLOWED_FORMATS_STR}"
VALIDATION_CATEGORY_IMAGE_REQUIRED = "Category image is required for upload"

# Category Error Messages
ERROR_CATEGORY_NOT_FOUND = "Category not found"
ERROR_CATEGORY_HAS_PRODUCTS = "Cannot delete category with associated products. Remove or reassign products first"
ERROR_CATEGORY_CREATE_FAILED = "Failed to create category"
ERROR_CATEGORY_UPDATE_FAILED = "Failed to update category"
ERROR_CATEGORY_IMAGE_UPLOAD_FAILED = "Failed to upload category image"
ERROR_CATEGORY_IMAGE_DELETE_FAILED = "Failed to delete category image"
ERROR_CATEGORY_CLOUDINARY_ERROR = "Error processing image with cloud storage"

# Category Success Messages
SUCCESS_CATEGORY_CREATED = "Category created successfully"
SUCCESS_CATEGORY_UPDATED = "Category updated successfully"
SUCCESS_CATEGORY_DELETED = "Category deleted successfully"
SUCCESS_CATEGORY_IMAGE_UPLOADED = "Category image uploaded successfully"
SUCCESS_CATEGORY_IMAGE_REMOVED = "Category image removed successfully"

# Category Search Constants
CATEGORY_SEARCH_MIN_QUERY_LENGTH = 2
CATEGORY_SEARCH_MAX_RESULTS = 50

# Category Search Messages
VALIDATION_SEARCH_QUERY_TOO_SHORT = f"Search query must be at least {CATEGORY_SEARCH_MIN_QUERY_LENGTH} characters"

# =============================================================================
# PRODUCT CONSTANTS
# =============================================================================

# Product Business Rules
PRODUCT_NAME_MIN_LENGTH = 2
PRODUCT_NAME_MAX_LENGTH = 200
PRODUCT_DESCRIPTION_MAX_LENGTH = 5000
PRODUCT_SLUG_MAX_LENGTH = 100
PRODUCT_PRICE_MIN_VALUE = 0
PRODUCT_PRICE_MAX_DIGITS = 10
PRODUCT_PRICE_DECIMAL_PLACES = 2
PRODUCT_STOCK_MIN_VALUE = 0
PRODUCT_WEIGHT_MIN_VALUE = 1  # in grams
PRODUCT_WEIGHT_MAX_VALUE = 100000  # 100kg in grams

# Product Validation Messages
VALIDATION_PRODUCT_NAME_REQUIRED = "Product name is required"
VALIDATION_PRODUCT_NAME_TOO_SHORT = f"Product name must be at least {PRODUCT_NAME_MIN_LENGTH} characters long"
VALIDATION_PRODUCT_NAME_TOO_LONG = f"Product name cannot exceed {PRODUCT_NAME_MAX_LENGTH} characters"
VALIDATION_PRODUCT_DESCRIPTION_REQUIRED = "Product description is required"
VALIDATION_PRODUCT_DESCRIPTION_TOO_LONG = f"Product description cannot exceed {PRODUCT_DESCRIPTION_MAX_LENGTH} characters"
VALIDATION_PRODUCT_PRICE_REQUIRED = "Product price is required"
VALIDATION_PRODUCT_PRICE_INVALID = f"Product price must be a positive number with max {PRODUCT_PRICE_MAX_DIGITS} digits and {PRODUCT_PRICE_DECIMAL_PLACES} decimal places"
VALIDATION_PRODUCT_STOCK_INVALID = "Product stock must be a non-negative integer"
VALIDATION_PRODUCT_CATEGORY_REQUIRED = "Product category is required"
VALIDATION_PRODUCT_BRAND_REQUIRED = "Product brand is required"
VALIDATION_PRODUCT_WEIGHT_INVALID = f"Product weight must be between {PRODUCT_WEIGHT_MIN_VALUE} and {PRODUCT_WEIGHT_MAX_VALUE} grams"

# Product Environmental Data Constants
PRODUCT_INGREDIENT_MAIN_MAX_LENGTH = 100
PRODUCT_CLIMATIQ_CATEGORY_MAX_LENGTH = 100
PRODUCT_ORIGIN_COUNTRY_LENGTH = 3  # ISO country code

# Product Environmental Choices
PRODUCT_BASE_TYPE_CHOICES = [
    ('water_based', 'Water Based'),
    ('plant_based', 'Plant Based'), 
    ('oil_based', 'Oil Based')
]

PRODUCT_PACKAGING_MATERIAL_CHOICES = [
    ('plastic_bottle', 'Plastic Bottle'),
    ('plastic_tube', 'Plastic Tube'),
    ('glass_container', 'Glass Container'),
    ('paper_wrap', 'Paper Wrap')
]

PRODUCT_TRANSPORTATION_TYPE_CHOICES = [
    ('air', 'Air'),
    ('sea', 'Sea'),
    ('land', 'Land')
]

PRODUCT_ECO_BADGE_CHOICES = [
    ('🌱 low Impact', 'Low Impact'),
    ('🌿 medium Impact', 'Medium Impact'),
    ('🌳 high Impact', 'High Impact')
]

# Product Carbon Footprint Constants
PRODUCT_CARBON_FOOTPRINT_MIN = 0.0
PRODUCT_CARBON_FOOTPRINT_MAX = 10000.0  # 10 tons CO2
PRODUCT_DEFAULT_CARBON_FOOTPRINT = 0.0

# Product Image Constants
PRODUCT_IMAGE_MAX_SIZE_MB = 10
PRODUCT_IMAGE_MAX_SIZE_BYTES = PRODUCT_IMAGE_MAX_SIZE_MB * 1024 * 1024
PRODUCT_IMAGE_ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
PRODUCT_IMAGE_ALLOWED_FORMATS_STR = ', '.join(PRODUCT_IMAGE_ALLOWED_EXTENSIONS).replace('.', '')

# Product Image Validation Messages
VALIDATION_PRODUCT_IMAGE_TOO_LARGE = f"Product image size cannot exceed {PRODUCT_IMAGE_MAX_SIZE_MB}MB"
VALIDATION_PRODUCT_IMAGE_INVALID_FORMAT = f"Unsupported image format. Allowed formats: {PRODUCT_IMAGE_ALLOWED_FORMATS_STR}"
VALIDATION_PRODUCT_PRIMARY_IMAGE_REQUIRED = "At least one primary image is required"

# Product Error Messages
ERROR_PRODUCT_NOT_FOUND = "Product not found"
ERROR_PRODUCT_CREATE_FAILED = "Failed to create product"
ERROR_PRODUCT_UPDATE_FAILED = "Failed to update product"
ERROR_PRODUCT_DELETE_FAILED = "Failed to delete product"
ERROR_PRODUCT_INACTIVE = "Product is not active"
ERROR_PRODUCT_OUT_OF_STOCK = "Product is out of stock"
ERROR_PRODUCT_IMAGE_UPLOAD_FAILED = "Failed to upload product image"
ERROR_PRODUCT_BRAND_MISMATCH = "Product does not belong to your brand"

# Product Success Messages
SUCCESS_PRODUCT_CREATED = "Product created successfully"
SUCCESS_PRODUCT_UPDATED = "Product updated successfully"
SUCCESS_PRODUCT_DELETED = "Product deleted successfully"
SUCCESS_PRODUCT_ACTIVATED = "Product activated successfully"
SUCCESS_PRODUCT_DEACTIVATED = "Product deactivated successfully"
SUCCESS_PRODUCT_IMAGE_UPLOADED = "Product image uploaded successfully"
SUCCESS_PRODUCT_IMAGE_REMOVED = "Product image removed successfully"

# Product Search Constants
PRODUCT_SEARCH_MIN_QUERY_LENGTH = 2
PRODUCT_SEARCH_MAX_RESULTS = 100

# =============================================================================
# GENERAL CONSTANTS
# =============================================================================

# API Response Status
STATUS_SUCCESS = "success"
STATUS_ERROR = "error"
STATUS_VALIDATION_ERROR = "validation_error"

# Pagination Constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Permission Messages
PERMISSION_DENIED = "You do not have permission to perform this action"
AUTHENTICATION_REQUIRED = "Authentication required"

# File Upload Constants
MAX_UPLOAD_SIZE_MB = 50
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Environmental Impact Constants
ECO_BADGE_THRESHOLD_LOW = 50.0    # kg CO2
ECO_BADGE_THRESHOLD_MEDIUM = 200.0  # kg CO2
ECO_BADGE_THRESHOLD_HIGH = 500.0   # kg CO2

# Climatiq API Defaults
DEFAULT_CLIMATIQ_CATEGORY = "consumer_goods-type_cosmetics_and_toiletries"