// ==========================================
//
// Description: auth Service
//
// File: authService.js
// Author: Anthony Bañon
// Created: 2025-11-18
// Last Updated: 2025-11-18
// Changes: Add login service functions
// ==========================================

import { api } from '../api';

export const authService = {
  // Login
  async login(username, password) {
    return await api.post('/auth/login/', { username, password });
  },

  // Cambiar contraseña
  async changePassword(current_password, new_password) {
    return await api.post('/auth/change-password/', {
      current_password,
      new_password,
    });
  },

  // Obtener perfil
  async getProfile() {
    return await api.get('/profile/');
  },

  // Logout
  async logout() {
    return await api.post('/auth/logout/');
  },
};
