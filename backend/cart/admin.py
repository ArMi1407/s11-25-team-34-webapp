"""
Django Admin Configuration for Cart
Basic admin interface for Django admin panel

File: admin.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

from django.contrib import admin
from .models import Cart, CartItem


##### Inline Admin Classes #####

class CartItemInline(admin.TabularInline):
    """Inline admin for CartItems within Cart"""
    model = CartItem
    extra = 0
    readonly_fields = ['total_price_display', 'total_carbon_display']
    fields = ['product', 'quantity', 'total_price_display', 'total_carbon_display', 'added_at_short']
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = "Total Price"
    
    def total_carbon_display(self, obj):
        return f"{obj.total_carbon:.2f} kg CO₂"
    total_carbon_display.short_description = "Total Carbon"
    
    def added_at_short(self, obj):
        return obj.added_at.strftime("%Y-%m-%d %H:%M")
    added_at_short.short_description = "Added"


##### Main Admin Classes #####

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin interface for Cart model"""
    
    list_display = ['id', 'user_or_session', 'total_items_display', 
                    'total_price_display', 'total_carbon_display', 
                    'created_at_short', 'updated_at_short']
    
    list_filter = ['created_at', 'updated_at']
    
    search_fields = ['user__username', 'user__email', 'session_key']
    
    readonly_fields = ['total_items_display', 'total_price_display', 
                       'total_carbon_display', 'created_at_display', 
                       'updated_at_display']
    
    fieldsets = [
        ('Cart Information', {
            'fields': ['user', 'session_key']
        }),
        ('Cart Totals', {
            'fields': ['total_items_display', 'total_price_display', 'total_carbon_display']
        }),
        ('Timestamps', {
            'fields': ['created_at_display', 'updated_at_display'],
            'classes': ['collapse']
        }),
    ]
    
    inlines = [CartItemInline]
    
    def user_or_session(self, obj):
        if obj.user:
            return f"User: {obj.user.username}"
        elif obj.session_key:
            return f"Guest: {obj.session_key[:10]}..."
        return "Anonymous"
    user_or_session.short_description = "Owner"
    
    def total_items_display(self, obj):
        return obj.total_items
    total_items_display.short_description = "Items"
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = "Total Price"
    
    def total_carbon_display(self, obj):
        return f"{obj.total_carbon_footprint:.2f} kg CO₂"
    total_carbon_display.short_description = "Carbon Footprint"
    
    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_short.short_description = "Created"
    
    def updated_at_short(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d")
    updated_at_short.short_description = "Updated"
    
    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_at_display.short_description = "Created At"
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    updated_at_display.short_description = "Updated At"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin interface for CartItem model"""
    
    list_display = ['cart_info', 'product', 'quantity', 'total_price_display', 
                    'total_carbon_display', 'added_at_short']
    
    list_filter = ['added_at', 'cart']
    
    search_fields = ['product__name', 'cart__user__username', 
                     'cart__session_key', 'product__brand_name']
    
    readonly_fields = ['total_price_display', 'total_carbon_display', 
                       'added_at_display']
    
    fieldsets = [
        ('Cart Item Information', {
            'fields': ['cart', 'product', 'quantity']
        }),
        ('Calculated Values', {
            'fields': ['total_price_display', 'total_carbon_display']
        }),
        ('Timestamps', {
            'fields': ['added_at_display'],
            'classes': ['collapse']
        }),
    ]
    
    def cart_info(self, obj):
        if obj.cart.user:
            return f"Cart #{obj.cart.id} ({obj.cart.user.username})"
        elif obj.cart.session_key:
            return f"Cart #{obj.cart.id} (Guest)"
        return f"Cart #{obj.cart.id}"
    cart_info.short_description = "Cart"
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = "Total Price"
    
    def total_carbon_display(self, obj):
        return f"{obj.total_carbon:.2f} kg CO₂"
    total_carbon_display.short_description = "Total Carbon"
    
    def added_at_short(self, obj):
        return obj.added_at.strftime("%Y-%m-%d %H:%M")
    added_at_short.short_description = "Added"
    
    def added_at_display(self, obj):
        return obj.added_at.strftime("%Y-%m-%d %H:%M:%S")
    added_at_display.short_description = "Added At"