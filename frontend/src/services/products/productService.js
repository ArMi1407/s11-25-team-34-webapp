// ==========================================
//
// Description: Product Service for Django API
//
// File: productService.js
// Author: Anthony Bañon
// Created: 2025-12-10
// Last Updated: 2025-12-10
// ==========================================

import { api } from '../api';

export const productService = {
  // Get all products
  async getAll(filters = {}) {
    const queryParams = new URLSearchParams();

    // Filter parameters based on Django ProductFilter
    if (filters.category) queryParams.append('category', filters.category);
    if (filters.category__slug)
      queryParams.append('category__slug', filters.category__slug);
    if (filters.brand) queryParams.append('brand', filters.brand);
    if (filters.min_price) queryParams.append('min_price', filters.min_price);
    if (filters.max_price) queryParams.append('max_price', filters.max_price);
    if (filters.base_type) queryParams.append('base_type', filters.base_type);
    if (filters.packaging_material)
      queryParams.append('packaging_material', filters.packaging_material);
    if (filters.eco_badge) queryParams.append('eco_badge', filters.eco_badge);
    if (filters.origin_country)
      queryParams.append('origin_country', filters.origin_country);
    if (filters.recyclable_packaging !== undefined)
      queryParams.append('recyclable_packaging', filters.recyclable_packaging);
    if (filters.min_carbon_footprint)
      queryParams.append('min_carbon_footprint', filters.min_carbon_footprint);
    if (filters.max_carbon_footprint)
      queryParams.append('max_carbon_footprint', filters.max_carbon_footprint);

    // Search and ordering
    if (filters.search) queryParams.append('search', filters.search);
    if (filters.ordering) queryParams.append('ordering', filters.ordering);

    // Pagination
    if (filters.page) queryParams.append('page', filters.page);
    if (filters.limit) queryParams.append('limit', filters.limit);

    // Show my products for brand owners
    if (filters.my_products === 'true')
      queryParams.append('my_products', 'true');

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/products/?${queryString}` : '/products/';

    return await api.get(endpoint);
  },

  // Get one product by slug
  async getOne(slug) {
    return await api.get(`/products/${slug}/`);
  },

  // Create a new product
  async create(data) {
    // Format data for Django
    const formattedData = {
      name: data.name,
      description: data.description || '',
      price: parseFloat(data.price),
      stock: parseInt(data.stock) || 0,
      category: data.category, // category ID
      brand: data.brand, // brand ID

      // Environmental data
      ingredient_main: data.ingredient_main || '',
      base_type: data.base_type || 'water_based',
      packaging_material: data.packaging_material || 'plastic_bottle',
      origin_country: data.origin_country || 'USA',
      weight: parseInt(data.weight) || 0,
      recyclable_packaging: Boolean(data.recyclable_packaging),
      transportation_type: data.transportation_type || 'land',
      climatiq_category:
        data.climatiq_category ||
        'consumer_goods-type_cosmetics_and_toiletries',

      // Calculated fields (optional, backend will calculate)
      carbon_footprint: parseFloat(data.carbon_footprint) || 0,
      eco_badge: data.eco_badge || '🌿 medium Impact',
    };

    // Handle image upload with FormData
    if (data.image && data.image instanceof File) {
      const formData = new FormData();
      Object.keys(formattedData).forEach((key) => {
        const value = formattedData[key];
        formData.append(
          key,
          typeof value === 'boolean'
            ? value.toString()
            : typeof value === 'number'
            ? value.toString()
            : value
        );
      });
      formData.append('image', data.image);

      return await api.request('/products/', {
        method: 'POST',
        body: formData,
      });
    }

    return await api.post('/products/', formattedData);
  },

  // Update product (full update)
  async update(slug, data) {
    const formattedData = { ...data };

    // Format numeric fields
    if (data.price) formattedData.price = parseFloat(data.price);
    if (data.stock) formattedData.stock = parseInt(data.stock);
    if (data.weight) formattedData.weight = parseInt(data.weight);
    if (data.carbon_footprint)
      formattedData.carbon_footprint = parseFloat(data.carbon_footprint);
    if (data.recyclable_packaging !== undefined)
      formattedData.recyclable_packaging = Boolean(data.recyclable_packaging);

    // Handle image upload with FormData
    if (data.image && data.image instanceof File) {
      const formData = new FormData();
      Object.keys(formattedData).forEach((key) => {
        if (key !== 'image') {
          const value = formattedData[key];
          formData.append(
            key,
            typeof value === 'boolean'
              ? value.toString()
              : typeof value === 'number'
              ? value.toString()
              : value
          );
        }
      });
      formData.append('image', data.image);

      return await api.request(`/products/${slug}/`, {
        method: 'PUT',
        body: formData,
      });
    }

    return await api.put(`/products/${slug}/`, formattedData);
  },

  // Update product (partial update)
  async updatePartial(slug, data) {
    const formattedData = { ...data };

    // Format numeric fields
    if (data.price) formattedData.price = parseFloat(data.price);
    if (data.stock) formattedData.stock = parseInt(data.stock);
    if (data.weight) formattedData.weight = parseInt(data.weight);
    if (data.carbon_footprint)
      formattedData.carbon_footprint = parseFloat(data.carbon_footprint);
    if (data.recyclable_packaging !== undefined)
      formattedData.recyclable_packaging = Boolean(data.recyclable_packaging);

    // Handle image upload with FormData
    if (data.image && data.image instanceof File) {
      const formData = new FormData();
      Object.keys(formattedData).forEach((key) => {
        if (key !== 'image') {
          const value = formattedData[key];
          formData.append(
            key,
            typeof value === 'boolean'
              ? value.toString()
              : typeof value === 'number'
              ? value.toString()
              : value
          );
        }
      });
      formData.append('image', data.image);

      return await api.request(`/products/${slug}/`, {
        method: 'PATCH',
        body: formData,
      });
    }

    return await api.patch(`/products/${slug}/`, formattedData);
  },

  // Delete product
  async delete(slug) {
    return await api.delete(`/products/${slug}/`);
  },

  // Get my products (for brand owners)
  async getMyProducts(filters = {}) {
    const queryParams = new URLSearchParams();

    // Add filters
    if (filters.search) queryParams.append('search', filters.search);
    if (filters.ordering) queryParams.append('ordering', filters.ordering);
    if (filters.page) queryParams.append('page', filters.page);
    if (filters.limit) queryParams.append('limit', filters.limit);

    const queryString = queryParams.toString();
    const endpoint = queryString
      ? `/products/my-products/?${queryString}`
      : '/products/my-products/';

    return await api.get(endpoint);
  },

  // Get similar products
  async getSimilarProducts(slug) {
    return await api.get(`/products/${slug}/similar/`);
  },

  // Upload/update product image
  async uploadImage(slug, imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    return await api.request(`/products/${slug}/upload-image/`, {
      method: 'PUT',
      body: formData,
    });
  },

  // Remove product image
  async removeImage(slug) {
    return await api.delete(`/products/${slug}/remove-image/`);
  },

  // Helper function to format product data for forms
  formatProductForForm(productData) {
    return {
      name: productData.name || '',
      description: productData.description || '',
      price: productData.price || 0,
      stock: productData.stock || 0,
      category: productData.category || '', // ID
      brand: productData.brand || '', // ID
      ingredient_main: productData.ingredient_main || '',
      base_type: productData.base_type || 'water_based',
      packaging_material: productData.packaging_material || 'plastic_bottle',
      origin_country: productData.origin_country || '',
      weight: productData.weight || 0,
      recyclable_packaging: productData.recyclable_packaging || true,
      transportation_type: productData.transportation_type || 'land',
      climatiq_category:
        productData.climatiq_category ||
        'consumer_goods-type_cosmetics_and_toiletries',
      // Note: carbon_footprint and eco_badge are calculated by backend
    };
  },

  // Helper function to format filters for UI
  formatFiltersForUI(filters) {
    const uiFilters = {};

    if (filters.category__slug) uiFilters.category = filters.category__slug;
    if (filters.min_price) uiFilters.minPrice = filters.min_price;
    if (filters.max_price) uiFilters.maxPrice = filters.max_price;
    if (filters.base_type) uiFilters.baseType = filters.base_type;
    if (filters.packaging_material)
      uiFilters.packaging = filters.packaging_material;
    if (filters.eco_badge) uiFilters.ecoBadge = filters.eco_badge;
    if (filters.origin_country) uiFilters.country = filters.origin_country;
    if (filters.recyclable_packaging !== undefined)
      uiFilters.recyclable = filters.recyclable_packaging;
    if (filters.min_carbon_footprint)
      uiFilters.minCarbon = filters.min_carbon_footprint;
    if (filters.max_carbon_footprint)
      uiFilters.maxCarbon = filters.max_carbon_footprint;
    if (filters.ordering) uiFilters.sortBy = filters.ordering;
    if (filters.search) uiFilters.search = filters.search;

    return uiFilters;
  },
};
