"""
Description: Category and Product Models
 
File: models.py
Author: Anthony Bañon
Created: 2025-11-29
Last Updated: 2025-12-03
Modify: Add image field to Category model
"""


from django.db import models
from accounts.models import BrandProfile
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100,  unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='categories/', blank=True, null=True,
        help_text="Representative image of the category"
    )
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    brand = models.ForeignKey(BrandProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    climatiq_category = models.CharField(
        max_length=100,
        blank=True,
        default="consumer_goods-type_cosmetics_and_toiletries",
        help_text="Technical category for API Climatiq"
    )

    # Price and Stock
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Datos ambientales (de tu CSV)
    ingredient_main = models.CharField(max_length=100)
    base_type = models.CharField(max_length=50, choices=[
        ('water_based', 'Water Based'),
        ('plant_based', 'Plant Based'), 
        ('oil_based', 'Oil Based')
    ])
    packaging_material = models.CharField(max_length=50, choices=[
        ('plastic_bottle', 'Plastic Bottle'),
        ('plastic_tube', 'Plastic Tube'),
        ('glass_container', 'Glass Container'),
        ('paper_wrap', 'Paper Wrap')
    ])
    origin_country = models.CharField(max_length=3)  # Country code
    weight = models.IntegerField()  # in grams
    recyclable_packaging = models.BooleanField(default=True)
    transportation_type = models.CharField(max_length=10, choices=[
        ('air', 'Air'),
        ('sea', 'Sea'),
        ('land', 'Land')
    ])
    
    # Calculated Environmental Footprints
    carbon_footprint = models.FloatField(default=0.0)  # kg CO2
    eco_badge = models.CharField(max_length=50, choices=[
        ('🌱 low Impact', 'Low Impact'),
        ('🌿 medium Impact', 'Medium Impact'),
        ('🌳 high Impact', 'High Impact')
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.product.name}"
