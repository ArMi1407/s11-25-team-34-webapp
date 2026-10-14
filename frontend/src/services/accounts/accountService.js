// ==========================================
//
// Account Service for User and Brand Management
//
// File: accountService.js
// Author: Anthony Bañon
// Created: 2025-12-11
// Last Updated: 2025-12-11
// ==========================================

import { api } from '../api';

export const accountService = {
  // ==================== USER PROFILE ====================

  // Register a new user
  async registerUser(userData) {
    return await api.post('/auth/register/', {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      password_confirm: userData.password_confirm,
      first_name: userData.first_name,
      last_name: userData.last_name,
      phone: userData.phone,
    });
  },

  // Get current user profile
  async getProfile() {
    return await api.get('/profile/');
  },

  // Update user profile (partial update)
  async updateProfile(data) {
    return await api.patch('/profile/update_profile/', data);
  },

  // Add eco points to user profile
  async addEcoPoints(points) {
    return await api.post('/profile/add_eco_points/', {
      points: points,
    });
  },

  // Delete user account
  async deleteAccount() {
    return await api.delete('/profile/delete_account/');
  },

  // ==================== BRAND PROFILE ====================

  // Register a brand
  async registerBrand(brandData) {
    return await api.post('/brand/register/', {
      brand_name: brandData.brand_name,
      sustainability_story: brandData.sustainability_story,
      manager_name: brandData.manager_name,
      manager_email: brandData.manager_email,
    });
  },

  // Get brand profile
  async getBrandProfile() {
    return await api.get('/brand/profile/');
  },

  // Update brand sustainability story
  async updateBrandStory(story) {
    return await api.put('/brand/story/', {
      sustainability_story: story,
    });
  },

  // Delete brand profile
  async deleteBrand() {
    return await api.delete('/brand/delete/');
  },

  // ==================== UTILITY METHODS ====================

  // Check if user is a brand manager
  async isBrandManager() {
    try {
      const profile = await this.getProfile();
      return profile?.is_brand_manager || false;
    } catch (error) {
      console.error('Error checking brand manager status:', error);
      return false;
    }
  },

  // Get user's eco points
  async getEcoPoints() {
    try {
      const profile = await this.getProfile();
      return profile?.eco_points || 0;
    } catch (error) {
      console.error('Error getting eco points:', error);
      return 0;
    }
  },

  // Get user's total carbon saved
  async getCarbonSaved() {
    try {
      const profile = await this.getProfile();
      return profile?.total_carbon_saved || 0;
    } catch (error) {
      console.error('Error getting carbon saved:', error);
      return 0;
    }
  },
};
