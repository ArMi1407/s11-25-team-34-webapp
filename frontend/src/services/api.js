// ==========================================
//
// Description: Api Service for Django Token Authentication
// Django provides a simple token that doesn't expire
//
// File: api.js
// Author: Anthony Bañon
// Updated: [Fecha actual]
// Changes: Adaptación para Django Token Authentication
// ==========================================

import { tokenInterceptor } from './auth/tokenInterceptor';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class Api {
  constructor() {
    this.baseURL = BASE_URL;
    this.tokenKey = 'auth_token';
    this.userKey = 'user_data';
  }

  // Get token from localStorage
  getToken() {
    return localStorage.getItem(this.tokenKey);
  }

  // Get user data from localStorage
  getUserData() {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }

  // Save auth data after successful login
  saveAuthData(responseData) {
    if (responseData.data && responseData.data.token) {
      // Save token
      localStorage.setItem(this.tokenKey, responseData.data.token);

      // Save user data (excluding token for security)
      const userData = { ...responseData.data };
      delete userData.token;
      localStorage.setItem(this.userKey, JSON.stringify(userData));

      return true;
    }
    return false;
  }

  // Clear auth data on logout
  clearAuthData() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  // Main request method
  async request(endpoint, options = {}) {
    const token = this.getToken();

    // Configuración base de headers
    const headers = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Token ${token}` }),
      ...options.headers,
    };

    const config = {
      ...options,
      headers,
      credentials: 'include',
    };

    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, config);

      if (!response.ok) {
        // Handle expired/invalid token
        if (response.status === 401) {
          console.log(
            'Token inválido o expirado. Limpiando datos de autenticación...'
          );

          // Clear auth data
          this.clearAuthData();

          // Redirect to login page
          tokenInterceptor.redirectToLogin();

          throw new Error('UNAUTHORIZED');
        }

        // Other errors
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message ||
            errorData.detail ||
            `Error ${response.status}: ${response.statusText}`
        );
      }

      // For login response, save token automatically
      if (endpoint.includes('/login') || endpoint.includes('/auth')) {
        const responseData = await response.json();
        this.saveAuthData(responseData);
        return responseData;
      }

      return await response.json();
    } catch (error) {
      // Log error for debugging
      console.error(`Error en petición ${endpoint}:`, error);

      // Don't throw if it's an unauthorized error that we already handled
      if (error.message === 'UNAUTHORIZED') {
        // Already handled by redirectToLogin
        throw new Error(
          'Sesión expirada. Por favor, inicie sesión nuevamente.'
        );
      }

      throw error;
    }
  }

  // Helper methods for different HTTP verbs
  get(endpoint, options = {}) {
    return this.request(endpoint, {
      method: 'GET',
      ...options,
    });
  }

  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options,
    });
  }

  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...options,
    });
  }

  patch(endpoint, data, options = {}) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
      ...options,
    });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, {
      method: 'DELETE',
      ...options,
    });
  }

  // Special method for file uploads (multipart/form-data)
  upload(endpoint, formData, options = {}) {
    const token = this.getToken();
    const headers = {
      ...(token && { Authorization: `Token ${token}` }),
      ...options.headers,
    };

    // Remove Content-Type for FormData to let browser set it
    delete headers['Content-Type'];

    return this.request(endpoint, {
      method: 'POST',
      body: formData,
      headers,
      ...options,
    });
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  }

  // Get current user data
  getCurrentUser() {
    return this.getUserData();
  }

  // Login method (convenience wrapper)
  async login(credentials) {
    return this.post('/login/', credentials);
  }

  // Logout method
  async logout() {
    try {
      // Call Django logout endpoint if it exists
      await this.post('/logout/');
    } catch (error) {
      console.warn('Logout API call failed:', error);
    } finally {
      this.clearAuthData();
      return true;
    }
  }
}

export const api = new Api();
