"""
Description: 
 
File: serislizers.py
Author: Anthony Bañon
Created: 2025-12-05
Last Updated: 2025-12-05
"""



from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cart, CartItem
from products.models import Product
from .constants import *
from django.db import transaction


##### Cart Item Serializers #####

class CartItemProductSerializer(serializers.ModelSerializer):
    """Formatting ONLY for product data in cart items"""
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id", "name", "price", "image_url"]
        read_only_fields = ["id", "name", "price", "image_url"]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    total_carbon = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'added_at', 'total_price', 'total_carbon']
        read_only_fields = fields

    def get_total_price(self, obj):
        return obj.total_price  # tu @property funciona bien

    def get_total_carbon(self, obj):
        return obj.total_carbon # tu @property funciona bien


class AddToCartSerializer(serializers.Serializer):
    """Validation ONLY for adding items to cart"""
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)
    
    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product does not exist")
        return value
    
    def validate_quantity(self, value):
        if value > MAX_CART_QUANTITY:
            raise serializers.ValidationError(f"Cannot add more than {MAX_CART_QUANTITY} of the same product")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """Validation ONLY for updating cart item quantity"""
    quantity = serializers.IntegerField(required=True, min_value=-MAX_CART_QUANTITY, max_value=MAX_CART_QUANTITY)
    
    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Quantity delta cannot be 0")
        return value


##### Cart Serializers #####

class CartSerializer(serializers.ModelSerializer):
    """Formatting ONLY for cart output"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_carbon_footprint = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'total_items', 'total_price', 'total_carbon_footprint', 
                  'created_at', 'updated_at', 'items']
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    """Validation ONLY for checkout"""
    shipping_address = serializers.JSONField(required=True)
    
    def validate_shipping_address(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Shipping address must be a JSON object")
        
        required_fields = ['street', 'city', 'state', 'postal_code', 'country']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        
        # Validate length of combined address
        address_str = str(value)
        if len(address_str) > MAX_SHIPPING_ADDRESS_LENGTH:
            raise serializers.ValidationError(f"Shipping address too long (max {MAX_SHIPPING_ADDRESS_LENGTH} characters)")
        
        return value