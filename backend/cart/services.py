"""
Cart Service layer ONLY for complex business logic

File: services.py  
Author: [Tu Nombre]
Created: 2025-12-01
"""

from django.db import transaction
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Cart, CartItem
from products.models import Product
from orders.models import Order, OrderItem, Payment
import uuid
from .constants import *
from datetime import datetime


class BusinessException(Exception):
    """Custom exception for business logic errors"""
    pass


class CartService:
    """
    Service ONLY for complex cart operations
    """
    
    def _get_or_create_cart(self, request):
        """Helper method to get or create cart based on user/session"""
        if request.user.is_authenticated:
            # User is logged in
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # Guest user with session
            if not request.session.session_key:
                request.session.create()
            
            session_key = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_key=session_key, 
                user=None
            )
        return cart
    
    
    def add_to_cart(self, request, product_id, quantity):
        """
        Complex operation: Add item to cart with business rules
        ASSUMES data already validated by serializer
        """
        cart = self._get_or_create_cart(request)

        # 1. Obtener el producto antes de usarlo
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise BusinessException("Product not found")

        # 2. Obtener o crear cart_item correctamente
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,  # ahora sí existe
            defaults={'quantity': 0}
        )

        # 3. Limite de items distintos
        if created and cart.items.count() > MAX_CART_ITEMS:
            raise BusinessException(
                f"Cannot have more than {MAX_CART_ITEMS} different items in cart"
            )

        # 4. Actualizar cantidad
        new_quantity = cart_item.quantity + quantity

        if new_quantity > MAX_CART_QUANTITY:
            raise BusinessException(
                f"Cannot have more than {MAX_CART_QUANTITY} of the same product"
            )

        # 5. Validar stock
        if hasattr(product, 'stock') and product.stock < new_quantity:
            raise BusinessException(f"Not enough stock. Available: {product.stock}")

        # 6. Guardar cambios
        cart_item.quantity = new_quantity
        cart_item.save()

        return cart_item
    
    
    def update_cart_item(self, request, item_id, quantity):
        """
        Complex operation: Update cart item quantity with business rules
        """
        try:
            cart = self._get_or_create_cart(request)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            raise BusinessException("Cart item not found")
        
        # Check product stock (if available)
        if hasattr(cart_item.product, 'stock') and cart_item.product.stock < quantity:
            raise BusinessException(f"Not enough stock. Available: {cart_item.product.stock}")
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return cart_item
    
    
    def remove_from_cart(self, request, item_id):
        """
        Complex operation: Remove item from cart
        """
        try:
            cart = self._get_or_create_cart(request)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            raise BusinessException("Cart item not found")
        
        cart_item.delete()
        return True
    
    
    def clear_cart(self, request):
        """
        Complex operation: Clear all items from cart
        """
        cart = self._get_or_create_cart(request)
        cart.items.all().delete()
        return True
    
    def get_cart(self, request):
        """
        Get cart with all items
        """
        return self._get_or_create_cart(request)
    
    @transaction.atomic
    def merge_carts(self, user, session_key):
        """
        Complex operation: Merge guest cart with user cart after login
        """
        warnings = []

        try:
            # Get guest cart
            guest_cart = Cart.objects.get(session_key=session_key, user=None)
            
            # Get or create user cart
            user_cart, created = Cart.objects.get_or_create(user=user)
            
            # Merge items
            for guest_item in guest_cart.items.all():
                user_item, item_created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=guest_item.product,
                    defaults={'quantity': 0}
                )
                
                new_quantity = user_item.quantity + guest_item.quantity
                
                # Check limits
                if new_quantity > MAX_CART_QUANTITY:
                    warnings.append(
                        f"El producto '{guest_item.product.name}' alcanzó la cantidad máxima "
                        f"({MAX_CART_QUANTITY}). Se ajustó automáticamente."
                    )
                    new_quantity = MAX_CART_QUANTITY

                user_item.quantity = new_quantity
                user_item.save()
            
            # Delete guest cart
            guest_cart.delete()
            
            return user_cart, warnings 
            
        except Cart.DoesNotExist:
            # No guest cart to merge
            cart, created = Cart.objects.get_or_create(user=user)
            return cart, []
    
    @transaction.atomic
    def checkout(self, request, shipping_address):
        """
        Complex operation: Convert cart to order with all business rules
        ASSUMES data already validated by serializer
        """
        cart = self._get_or_create_cart(request)
        
        # Validate cart is not empty
        if cart.total_items == 0:
            raise BusinessException("Cannot checkout with empty cart")
        
        # Check all products have enough stock
        for item in cart.items.all():
            if hasattr(item.product, 'stock') and item.product.stock < item.quantity:
                raise BusinessException(f"Not enough stock for {item.product.name}. Available: {item.product.stock}")
        
        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            order_number=order_number,
            status='pending',
            total_amount=cart.total_price,
            total_carbon_footprint=cart.total_carbon_footprint,
            shipping_address=shipping_address
        )
        
        # Create order items and update product stock
        for cart_item in cart.items.all():
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
                carbon_footprint=cart_item.product.carbon_footprint
            )
            
            # Update product stock (if stock field exists)
            if hasattr(cart_item.product, 'stock'):
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
        
        # Clear the cart
        cart.items.all().delete()
        
        return order