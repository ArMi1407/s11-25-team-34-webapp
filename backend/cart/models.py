# cart/models.py
from django.db import models
from products.models import Product
from django.db.models import Sum, F, FloatField, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)  # Para usuarios no logueados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_items(self):
        return self.items.aggregate(total=Coalesce(Sum('quantity'), 0))['total']
    
    @property
    def total_price(self):
        return self.items.aggregate(
            total=Coalesce(
                Sum(F('quantity') * F('product__price'), output_field=DecimalField(max_digits=12, decimal_places=2)),
                Decimal('0.00')
            )
        )['total']
    
    @property
    def total_carbon_footprint(self):
        return self.items.aggregate(
            total=Coalesce(
                Sum(F('quantity') * F('product__carbon_footprint'), output_field=FloatField()),
                0.0
            )
        )['total']
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest Cart {self.session_key}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True) # Fecha en que se añadió el ítem al carrito
    
    class Meta:
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["product"]),
        ]

    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    @property
    def total_carbon(self):
        return self.product.carbon_footprint * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
