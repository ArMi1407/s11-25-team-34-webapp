// ==========================================
//
// Description: Category Service for Django API
//
// File: categoryService.js
// Author: Anthony Bañon
// Created: 2025-12-10
// Last Updated: 2025-12-10
// ==========================================

import { api } from '../api';

export const categoryService = {
  // Get all categories
  async getAll(filters = {}) {
    // Manage query parameters for filters
    const queryParams = new URLSearchParams();

    // Add filters if they exist (based on Django ViewSet)
    if (filters.slug) queryParams.append('slug', filters.slug);
    if (filters.search) queryParams.append('search', filters.search);
    if (filters.ordering) queryParams.append('ordering', filters.ordering);
    if (filters.page) queryParams.append('page', filters.page);
    if (filters.limit) queryParams.append('limit', filters.limit);

    // Construct the final endpoint with query parameters
    const queryString = queryParams.toString();
    const endpoint = queryString
      ? `/categories/?${queryString}`
      : '/categories/';

    return await api.get(endpoint);
  },

  // Get one category by slug
  async getOne(slug) {
    return await api.get(`/categories/${slug}/`);
  },

  // Create a new category
  async create(data) {
    // Handle image upload with FormData
    if (data.image && data.image instanceof File) {
      const formData = new FormData();
      formData.append('name', data.name);
      formData.append('description', data.description || '');
      if (data.slug) formData.append('slug', data.slug);
      formData.append('image', data.image);

      return await api.request('/categories/', {
        method: 'POST',
        body: formData,
      });
    }

    return await api.post('/categories/', data);
  },

  // Update category (full update)
  async update(slug, data) {
    // Handle image upload with FormData
    if (data.image && data.image instanceof File) {
      const formData = new FormData();
      formData.append('name', data.name);
      formData.append('description', data.description || '');
      if (data.slug) formData.append('slug', data.slug);
      formData.append('image', data.image);

      return await api.request(`/categories/${slug}/`, {
        method: 'PUT',
        body: formData,
      });
    }

    return await api.put(`/categories/${slug}/`, data);
  },

  // Update category (partial update)
  async updatePartial(slug, data) {
    // Handle image upload with FormData
    if (data.image && data.image instanceof File) {
      const formData = new FormData();
      Object.keys(data).forEach((key) => {
        if (key !== 'image') {
          const value = data[key];
          // Convert numbers to strings for FormData
          formData.append(
            key,
            typeof value === 'number' ? value.toString() : value
          );
        }
      });
      formData.append('image', data.image);

      return await api.request(`/categories/${slug}/`, {
        method: 'PATCH',
        body: formData,
      });
    }

    return await api.patch(`/categories/${slug}/`, data);
  },

  // Delete category
  async delete(slug) {
    return await api.delete(`/categories/${slug}/`);
  },

  // Upload/update category image
  async uploadImage(slug, imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);

    return await api.request(`/categories/${slug}/upload-image/`, {
      method: 'PUT',
      body: formData,
    });
  },

  // Remove category image
  async removeImage(slug) {
    return await api.delete(`/categories/${slug}/remove-image/`);
  },

  // Get products by category
  async getProductsByCategory(slug, filters = {}) {
    const queryParams = new URLSearchParams();

    // Add filters for products
    if (filters.search) queryParams.append('search', filters.search);
    if (filters.ordering) queryParams.append('ordering', filters.ordering);
    if (filters.page) queryParams.append('page', filters.page);
    if (filters.limit) queryParams.append('limit', filters.limit);

    const queryString = queryParams.toString();
    const endpoint = queryString
      ? `/categories/${slug}/products/?${queryString}`
      : `/categories/${slug}/products/`;

    return await api.get(endpoint);
  },
};
