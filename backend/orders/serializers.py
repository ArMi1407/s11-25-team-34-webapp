"""
Orders Serializers ONLY for validation and formatting

File: serializers.py
Author: Anthony Bañon
Created: 2025-12-05
Last Updated: 2025-12-05
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Order, OrderItem, Payment
from products.models import Product
from .constants import *
import json


##### Order Item Serializers #####

class OrderItemProductSerializer(serializers.ModelSerializer):
    """Formatting ONLY for product data in order items"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand_name', 'image_url']
        read_only_fields = fields


class OrderItemSerializer(serializers.ModelSerializer):
    """Formatting ONLY for order item output"""
    product = OrderItemProductSerializer(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'carbon_footprint', 'total_price']
        read_only_fields = fields


##### Order Serializers #####

class OrderSerializer(serializers.ModelSerializer):
    """Formatting ONLY for order output"""
    items = OrderItemSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    payment_status = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'user', 'username', 'email',
            'total_amount', 'total_carbon_footprint', 'shipping_address',
            'created_at', 'updated_at', 'items', 'payment_status', 'payment_method'
        ]
        read_only_fields = fields
    
    def get_payment_status(self, obj):
        try:
            payment = Payment.objects.get(order=obj)
            return payment.status
        except Payment.DoesNotExist:
            return 'unpaid'
    
    def get_payment_method(self, obj):
        try:
            payment = Payment.objects.get(order=obj)
            return payment.payment_method
        except Payment.DoesNotExist:
            return None


class OrderCreateSerializer(serializers.Serializer):
    """Validation ONLY for order creation"""
    shipping_address = serializers.JSONField(required=True)
    
    def validate_shipping_address(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Shipping address must be a JSON object")
        
        required_fields = ['street', 'city', 'state', 'postal_code', 'country']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        
        # Validate length
        address_str = json.dumps(value)
        if len(address_str) > MAX_SHIPPING_ADDRESS_LENGTH:
            raise serializers.ValidationError(f"Shipping address too long")
        
        return value


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Validation ONLY for order status update (admin only)"""
    status = serializers.ChoiceField(choices=ORDER_STATUS_CHOICES, required=True)
    
    def validate_status(self, value):
        # Prevent invalid status transitions could be added here
        return value


class OrderCancelSerializer(serializers.Serializer):
    """Validation ONLY for order cancellation"""
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


##### Payment Serializers #####

class PaymentSerializer(serializers.ModelSerializer):
    """Formatting ONLY for payment output"""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'payment_method', 'transaction_id',
            'amount', 'status', 'paid_at', 'created_at'
        ]
        read_only_fields = fields


class PaymentCreateSerializer(serializers.Serializer):
    """Validation ONLY for payment creation"""
    payment_method = serializers.ChoiceField(choices=PAYMENT_METHOD_CHOICES, required=True)
    
    def validate_payment_method(self, value):
        if value not in [pm[0] for pm in PAYMENT_METHOD_CHOICES]:
            raise serializers.ValidationError(ERROR_INVALID_PAYMENT_METHOD)
        return value


class PaymentUpdateSerializer(serializers.Serializer):
    """Validation ONLY for payment status update (webhook/callback)"""
    transaction_id = serializers.CharField(required=False, max_length=MAX_TRANSACTION_ID_LENGTH)
    status = serializers.ChoiceField(choices=PAYMENT_STATUS_CHOICES, required=True)
    
    def validate_transaction_id(self, value):
        if len(value) > MAX_TRANSACTION_ID_LENGTH:
            raise serializers.ValidationError(f"Transaction ID too long")
        return value