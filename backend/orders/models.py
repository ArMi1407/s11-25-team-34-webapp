# orders/models.py
from django.db import models
from products.models import Product
from .constants import *

class Order(models.Model):
    ORDER_STATUS = ORDER_STATUS_CHOICES
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    
    # Totales
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_carbon_footprint = models.FloatField(default=0.0)
    
    # Dirección de envío
    shipping_address = models.JSONField()  # Almacena dirección como JSON
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio al momento de la compra
    carbon_footprint = models.FloatField()  # Huella al momento de la compra
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Payment(models.Model):
    PAYMENT_METHODS = PAYMENT_METHOD_CHOICES
    
    PAYMENT_STATUS = PAYMENT_STATUS_CHOICES
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment for Order {self.order.order_number}"
