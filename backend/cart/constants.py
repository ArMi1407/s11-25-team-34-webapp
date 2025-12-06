"""
Cart Constants

File: constants.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

# Cart limits
MAX_CART_QUANTITY = 100  # Maximum quantity per product in cart
MAX_CART_ITEMS = 50  # Maximum number of different items in cart
MAX_SHIPPING_ADDRESS_LENGTH = 500

# Error messages
ERROR_CART_EMPTY = "Cannot perform this operation with an empty cart"
ERROR_PRODUCT_NOT_FOUND = "Product not found"
ERROR_NOT_ENOUGH_STOCK = "Not enough stock available"
ERROR_CART_LIMIT_EXCEEDED = "Cart limit exceeded"
ERROR_ITEM_NOT_IN_CART = "Item not found in cart"

# Success messages
SUCCESS_ITEM_ADDED = "Item added to cart successfully"
SUCCESS_ITEM_UPDATED = "Cart item updated successfully"
SUCCESS_ITEM_REMOVED = "Item removed from cart"
SUCCESS_CART_CLEARED = "Cart cleared successfully"
SUCCESS_CHECKOUT = "Order created successfully"
SUCCESS_CART_MERGED = "Cart merged successfully"