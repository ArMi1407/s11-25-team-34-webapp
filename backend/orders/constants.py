"""
Description: Constants
 
File: constants.py
Author: Anthony Bañon
Created: 2025-12-05
Last Updated: 2025-12-05
"""



# Order statuses
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_PAID = 'paid'
ORDER_STATUS_SHIPPED = 'shipped'
ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_CANCELLED = 'cancelled'

ORDER_STATUS_CHOICES = [
    (ORDER_STATUS_PENDING, 'Pending'),
    (ORDER_STATUS_PAID, 'Paid'),
    (ORDER_STATUS_SHIPPED, 'Shipped'),
    (ORDER_STATUS_DELIVERED, 'Delivered'),
    (ORDER_STATUS_CANCELLED, 'Cancelled'),
]

# Payment methods
PAYMENT_METHOD_STRIPE = 'stripe'
PAYMENT_METHOD_MERCADOPAGO = 'mercadopago'

PAYMENT_METHOD_CHOICES = [
    (PAYMENT_METHOD_STRIPE, 'Stripe'),
    (PAYMENT_METHOD_MERCADOPAGO, 'MercadoPago'),
]

# Payment statuses
PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_PAID = 'paid'
PAYMENT_STATUS_CANCELLED = 'cancelled'

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS_PENDING, 'Pending'),
    (PAYMENT_STATUS_PAID, 'Paid'),
    (PAYMENT_STATUS_CANCELLED, 'Cancelled'),
]

# Limits
MAX_TRANSACTION_ID_LENGTH = 100
MAX_ORDER_NUMBER_LENGTH = 20
MAX_SHIPPING_ADDRESS_LENGTH = 500

# Error messages
ERROR_ORDER_NOT_FOUND = "Order not found"
ERROR_ORDER_CANCELLED = "Order is already cancelled"
ERROR_ORDER_NOT_PENDING = "Order cannot be cancelled (not in pending status)"
ERROR_PAYMENT_NOT_FOUND = "Payment not found"
ERROR_PAYMENT_ALREADY_PAID = "Payment is already completed"
ERROR_INVALID_PAYMENT_METHOD = "Invalid payment method"
ERROR_INSUFFICIENT_PERMISSION = "You don't have permission to access this order"

# Success messages
SUCCESS_ORDER_CREATED = "Order created successfully"
SUCCESS_ORDER_CANCELLED = "Order cancelled successfully"
SUCCESS_PAYMENT_CREATED = "Payment created successfully"
SUCCESS_PAYMENT_UPDATED = "Payment updated successfully"
SUCCESS_ORDER_STATUS_UPDATED = "Order status updated successfully"