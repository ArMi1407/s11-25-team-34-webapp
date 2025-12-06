"""
Django Admin Configuration for Orders
Basic admin interface for Django admin panel

File: admin.py
Author: [Tu Nombre]
Created: 2025-12-01
"""

from django.contrib import admin
from .models import Order, OrderItem, Payment


##### Inline Admin Classes #####

class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItems"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price', 'total_carbon']
    fields = ['product', 'quantity', 'price', 'total_price', 'carbon_footprint', 'total_carbon']
    
    def total_price(self, obj):
        return f"${obj.total_price:.2f}"
    total_price.short_description = "Total Price"
    
    def total_carbon(self, obj):
        total = obj.carbon_footprint * obj.quantity
        return f"{total:.2f} kg CO₂"
    total_carbon.short_description = "Total Carbon"


class PaymentInline(admin.StackedInline):
    """Inline admin for Payment"""
    model = Payment
    extra = 0
    readonly_fields = ['created', 'modified']
    fields = ['payment_method', 'transaction_id', 'amount', 'status', 'paid_at', 'created', 'modified']
    
    def created(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else "-"
    created.short_description = "Created"
    
    def modified(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(obj, 'updated_at') else "-"
    modified.short_description = "Modified"


##### Main Admin Classes #####

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model"""
    
    list_display = ['order_number', 'user', 'status', 'total_amount_display', 
                    'total_carbon_display', 'created_at_short']
    
    list_filter = ['status', 'created_at', 'updated_at']
    
    search_fields = ['order_number', 'user__username', 'user__email']
    
    readonly_fields = ['order_number', 'total_amount_display', 'total_carbon_display',
                       'created_at_display', 'updated_at_display', 'shipping_address_display']
    
    fieldsets = [
        ('Order Information', {
            'fields': ['order_number', 'user', 'status']
        }),
        ('Totals', {
            'fields': ['total_amount_display', 'total_carbon_display']
        }),
        ('Shipping', {
            'fields': ['shipping_address_display']
        }),
        ('Timestamps', {
            'fields': ['created_at_display', 'updated_at_display'],
            'classes': ['collapse']
        }),
    ]
    
    inlines = [OrderItemInline, PaymentInline]
    
    def total_amount_display(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_display.short_description = "Total Amount"
    
    def total_carbon_display(self, obj):
        return f"{obj.total_carbon_footprint:.2f} kg CO₂"
    total_carbon_display.short_description = "Carbon Footprint"
    
    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_short.short_description = "Created"
    
    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_at_display.short_description = "Created At"
    
    def updated_at_display(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")
    updated_at_display.short_description = "Updated At"
    
    def shipping_address_display(self, obj):
        import json
        try:
            address = obj.shipping_address
            if isinstance(address, str):
                address = json.loads(address)
            
            formatted_lines = []
            for key, value in address.items():
                formatted_lines.append(f"<strong>{key.title()}:</strong> {value}")
            
            return "<br>".join(formatted_lines)
        except:
            return str(obj.shipping_address)
    shipping_address_display.short_description = "Shipping Address"
    shipping_address_display.allow_tags = True


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem model"""
    
    list_display = ['order', 'product', 'quantity', 'price_display', 
                    'total_price_display', 'carbon_display']
    
    list_filter = ['order', 'product']
    
    search_fields = ['order__order_number', 'product__name']
    
    readonly_fields = ['total_price_display', 'total_carbon_display']
    
    def price_display(self, obj):
        return f"${obj.price:.2f}"
    price_display.short_description = "Unit Price"
    
    def total_price_display(self, obj):
        return f"${obj.total_price:.2f}"
    total_price_display.short_description = "Total Price"
    
    def carbon_display(self, obj):
        total = obj.carbon_footprint * obj.quantity
        return f"{total:.2f} kg CO₂"
    carbon_display.short_description = "Total Carbon"
    
    def total_carbon_display(self, obj):
        total = obj.carbon_footprint * obj.quantity
        return f"{total:.2f} kg CO₂"
    total_carbon_display.short_description = "Total Carbon"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model"""
    
    list_display = ['order', 'payment_method', 'status', 'amount_display', 
                    'paid_at_short', 'transaction_id_short']
    
    list_filter = ['status', 'payment_method', 'paid_at']
    
    search_fields = ['order__order_number', 'transaction_id']
    
    readonly_fields = ['order_link', 'amount_display', 'paid_at_display']
    
    fieldsets = [
        ('Payment Information', {
            'fields': ['order_link', 'payment_method', 'status', 'amount_display']
        }),
        ('Transaction Details', {
            'fields': ['transaction_id', 'paid_at_display']
        }),
    ]
    
    def amount_display(self, obj):
        return f"${obj.amount:.2f}"
    amount_display.short_description = "Amount"
    
    def paid_at_short(self, obj):
        return obj.paid_at.strftime("%Y-%m-%d") if obj.paid_at else "-"
    paid_at_short.short_description = "Paid At"
    
    def paid_at_display(self, obj):
        return obj.paid_at.strftime("%Y-%m-%d %H:%M:%S") if obj.paid_at else "-"
    paid_at_display.short_description = "Paid At"
    
    def transaction_id_short(self, obj):
        if obj.transaction_id and len(obj.transaction_id) > 15:
            return f"{obj.transaction_id[:15]}..."
        return obj.transaction_id or "-"
    transaction_id_short.short_description = "Transaction ID"
    
    def order_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse
        
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = "Order"
    order_link.allow_tags = True
