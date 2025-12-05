"""
Description: Category and Product Admin Configuration

File: admin.py
Author: Anthony Bañon
Created: 2025-12-06
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'image_preview', 'product_count']
    list_filter = ['name']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Products'


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'brand', 
        'category', 
        'price', 
        'stock', 
        'is_active', 
        'carbon_footprint',
        'eco_badge',
        'image_preview'
    ]
    list_filter = [
        'is_active', 
        'category', 
        'base_type', 
        'packaging_material',
        'eco_badge',
        'created_at'
    ]
    search_fields = [
        'name', 
        'description', 
        'ingredient_main',
        'brand__user__email',
        'brand__brand_name'
    ]
    readonly_fields = [
        'slug', 
        'carbon_footprint', 
        'eco_badge',
        'image_preview',
        'created_at',
        'updated_at'
    ]
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_active']
    list_per_page = 20
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'image', 'image_preview')
        }),
        ('Business Information', {
            'fields': ('brand', 'category', 'price', 'stock', 'is_active')
        }),
        ('Product Characteristics', {
            'fields': (
                'ingredient_main',
                'base_type',
                'packaging_material',
                'origin_country',
                'weight',
                'recyclable_packaging',
                'transportation_type'
            )
        }),
        ('Environmental Data', {
            'fields': (
                'carbon_footprint',
                'eco_badge',
                'climatiq_category'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('brand', 'category')
        return queryset


# Register models
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
