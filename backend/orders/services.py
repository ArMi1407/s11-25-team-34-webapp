"""
Orders Service layer ONLY for complex business logic

File: services.py  
Author: Anthony Bañon
Created: 2025-12-05
Last Updated: 2025-12-05
"""

from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Order, OrderItem, Payment
from products.models import Product
from .constants import *
import uuid


class BusinessException(Exception):
    """Custom exception for business logic errors"""
    pass


class OrderService:
    """
    Service ONLY for complex order operations
    """
    
    @transaction.atomic
    def create_order_from_cart(self, user, cart, shipping_address):
        """
        Complex operation: Create order from cart items
        ASSUMES data already validated by serializer
        """
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate totals from cart
        total_amount = cart.total_price
        total_carbon_footprint = cart.total_carbon_footprint
        
        # Create order
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            status=ORDER_STATUS_PENDING,
            total_amount=total_amount,
            total_carbon_footprint=total_carbon_footprint,
            shipping_address=shipping_address
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                carbon_footprint=cart_item.product.carbon_footprint
            )
            
            # Update product stock if exists
            if hasattr(cart_item.product, 'stock'):
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
        
        return order
    
    def get_user_orders(self, user):
        """
        Get all orders for a user
        """
        return Order.objects.filter(user=user).order_by('-created_at')
    
    def get_order_by_id(self, user, order_id):
        """
        Get specific order with permission check
        """
        try:
            order = Order.objects.get(id=order_id)
            # Check permission
            if order.user != user and not user.is_staff:
                raise BusinessException(ERROR_INSUFFICIENT_PERMISSION)
            return order
        except Order.DoesNotExist:
            raise BusinessException(ERROR_ORDER_NOT_FOUND)
    
    @transaction.atomic
    def cancel_order(self, user, order_id, reason=""):
        """
        Complex operation: Cancel order with business rules
        """
        order = self.get_order_by_id(user, order_id)
        
        # Check if order can be cancelled
        if order.status == ORDER_STATUS_CANCELLED:
            raise BusinessException(ERROR_ORDER_CANCELLED)
        
        if order.status != ORDER_STATUS_PENDING:
            raise BusinessException(ERROR_ORDER_NOT_PENDING)
        
        # Update order status
        order.status = ORDER_STATUS_CANCELLED
        order.save()
        
        # Restore product stock if exists
        for order_item in order.items.all():
            if hasattr(order_item.product, 'stock'):
                order_item.product.stock += order_item.quantity
                order_item.product.save()
        
        return order
    
    def get_order_status_history(self, order):
        """
        Get status history for an order (could be extended with a StatusHistory model)
        """
        # For now, return basic status info
        return {
            'current_status': order.status,
            'created_at': order.created_at,
            'updated_at': order.updated_at
        }


class PaymentService:
    """
    Service ONLY for complex payment operations
    """
    
    @transaction.atomic
    def create_payment(self, order, payment_method):
        """
        Complex operation: Create payment for an order
        ASSUMES data already validated by serializer
        """
        # Check if payment already exists
        if Payment.objects.filter(order=order).exists():
            payment = Payment.objects.get(order=order)
            if payment.status == PAYMENT_STATUS_PAID:
                raise BusinessException(ERROR_PAYMENT_ALREADY_PAID)
            return payment
        
        # Create new payment
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=order.total_amount,
            status=PAYMENT_STATUS_PENDING
        )
        
        return payment
    
    @transaction.atomic
    def update_payment_status(self, order, transaction_id, status):
        """
        Complex operation: Update payment status (for webhooks/callbacks)
        """
        try:
            payment = Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            raise BusinessException(ERROR_PAYMENT_NOT_FOUND)
        
        # Update payment
        payment.transaction_id = transaction_id
        payment.status = status
        
        if status == PAYMENT_STATUS_PAID:
            payment.paid_at = timezone.now()
            
            # Update order status
            order.status = ORDER_STATUS_PAID
            order.save()
        
        elif status == PAYMENT_STATUS_CANCELLED:
            # Optionally update order status if payment cancelled
            if order.status == ORDER_STATUS_PENDING:
                order.status = ORDER_STATUS_CANCELLED
                order.save()
        
        payment.save()
        
        return payment, order
    
    def get_order_payment(self, order):
        """
        Get payment for an order
        """
        try:
            return Payment.objects.get(order=order)
        except Payment.DoesNotExist:
            return None


class AdminOrderService:
    """
    Service ONLY for admin order operations
    """
    
    @transaction.atomic
    def update_order_status(self, order_id, new_status):
        """
        Complex operation: Admin updates order status
        """
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise BusinessException(ERROR_ORDER_NOT_FOUND)
        
        # Validate status transition logic
        valid_transitions = {
            ORDER_STATUS_PENDING: [ORDER_STATUS_PAID, ORDER_STATUS_CANCELLED],
            ORDER_STATUS_PAID: [ORDER_STATUS_SHIPPED, ORDER_STATUS_CANCELLED],
            ORDER_STATUS_SHIPPED: [ORDER_STATUS_DELIVERED],
            ORDER_STATUS_DELIVERED: [],
            ORDER_STATUS_CANCELLED: [],
        }
        
        current_status = order.status
        if new_status not in valid_transitions.get(current_status, []):
            raise BusinessException(f"Cannot transition from {current_status} to {new_status}")
        
        # Update order
        order.status = new_status
        order.save()
        
        return order
    
    def get_all_orders(self, filters=None):
        """
        Get all orders with optional filters
        """
        queryset = Order.objects.all().order_by('-created_at')
        
        if filters:
            status = filters.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            date_from = filters.get('date_from')
            if date_from:
                queryset = queryset.filter(created_at__gte=date_from)
            
            date_to = filters.get('date_to')
            if date_to:
                queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset