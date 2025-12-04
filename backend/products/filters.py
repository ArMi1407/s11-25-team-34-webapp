"""
Description: Product Filters

File: filters.py
Author: [Your Name]
Created: 2025-12-03
Last Updated: 2025-12-03
"""

import django_filters
from django.db.models import Q
from .models import Product, Category
from .constants import *

class ProductFilter(django_filters.FilterSet):
    """
    FilterSet for advanced product filtering
    """
    # Basic filters
    name = django_filters.CharFilter(
        field_name='name', 
        lookup_expr='icontains',
        help_text="Filter by product name (case-insensitive)"
    )
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category',
        help_text="Filter by category ID"
    )
    
    category_slug = django_filters.CharFilter(
        field_name='category__slug',
        lookup_expr='exact',
        help_text="Filter by category slug"
    )
    
    # Price range filters
    min_price = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='gte',
        help_text="Minimum price"
    )
    
    max_price = django_filters.NumberFilter(
        field_name='price', 
        lookup_expr='lte',
        help_text="Maximum price"
    )
    
    # Stock filters
    in_stock = django_filters.BooleanFilter(
        method='filter_in_stock',
        help_text="Filter products in stock (stock > 0)"
    )
    
    # Environmental filters
    base_type = django_filters.ChoiceFilter(
        choices=PRODUCT_BASE_TYPE_CHOICES,
        help_text="Filter by product base type"
    )
    
    packaging_material = django_filters.ChoiceFilter(
        choices=PRODUCT_PACKAGING_MATERIAL_CHOICES,
        help_text="Filter by packaging material"
    )
    
    recyclable = django_filters.BooleanFilter(
        field_name='recyclable_packaging',
        help_text="Filter by recyclable packaging"
    )
    
    transportation_type = django_filters.ChoiceFilter(
        choices=PRODUCT_TRANSPORTATION_TYPE_CHOICES,
        help_text="Filter by transportation type"
    )
    
    # Carbon footprint filters
    max_carbon = django_filters.NumberFilter(
        field_name='carbon_footprint',
        lookup_expr='lte',
        help_text="Maximum carbon footprint (kg CO2)"
    )
    
    eco_badge = django_filters.ChoiceFilter(
        choices=PRODUCT_ECO_BADGE_CHOICES,
        help_text="Filter by eco badge"
    )
    
    # Ingredient filter
    ingredient = django_filters.CharFilter(
        field_name='ingredient_main',
        lookup_expr='icontains',
        help_text="Filter by main ingredient"
    )
    
    # Brand filter
    brand = django_filters.CharFilter(
        field_name='brand__name',
        lookup_expr='icontains',
        help_text="Filter by brand name"
    )
    
    # Weight range filters
    min_weight = django_filters.NumberFilter(
        field_name='weight',
        lookup_expr='gte',
        help_text="Minimum weight in grams"
    )
    
    max_weight = django_filters.NumberFilter(
        field_name='weight',
        lookup_expr='lte',
        help_text="Maximum weight in grams"
    )
    
    # Search query (combined multiple fields)
    q = django_filters.CharFilter(
        method='filter_search',
        help_text="Search in name, description, and ingredients"
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'category_slug', 'brand',
            'min_price', 'max_price', 'in_stock',
            'base_type', 'packaging_material', 'recyclable',
            'transportation_type', 'max_carbon', 'eco_badge',
            'ingredient', 'min_weight', 'max_weight', 'q'
        ]
    
    def filter_in_stock(self, queryset, name, value):
        """
        Filter products based on stock availability
        """
        if value is True:
            return queryset.filter(stock__gt=0)
        elif value is False:
            return queryset.filter(stock=0)
        return queryset
    
    def filter_search(self, queryset, name, value):
        """
        Search across multiple fields: name, description, ingredients, and brand
        """
        if not value or len(value) < PRODUCT_SEARCH_MIN_QUERY_LENGTH:
            return queryset
        
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(ingredient_main__icontains=value) |
            Q(brand__name__icontains=value)
        )
    
    @property
    def qs(self):
        """
        Override to apply additional filtering logic
        """
        queryset = super().qs
        
        # For non-authenticated users or regular list views, only show active products
        request = self.request
        if not request or not request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        else:
            # For authenticated users, check if they want to see all their products
            # (including inactive ones for brand owners)
            if hasattr(request.user, 'brandprofile'):
                show_all = request.query_params.get('show_all', 'false').lower() == 'true'
                if not show_all and not request.query_params.get('my_products'):
                    queryset = queryset.filter(is_active=True)
        
        return queryset