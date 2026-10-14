// ==========================================
//
// Description: Token Interceptor for Django Token Authentication
// Django provides a simple token that doesn't expire (or has very long expiration)
//
// File: tokenInterceptor.js
// Author: Anthony Bañon
// Created: 2025-12-08
// Last Updated: 2025-12-08
// ==========================================

class TokenInterceptor {
  constructor() {
    this.authFunctions = null;
    this.tokenStorageKey = 'auth_token';
    this.userStorageKey = 'user_data';
  }

  // Set auth functions from AuthContext
  setAuthFunctions(functions) {
    this.authFunctions = functions;
  }

  // Get token from localStorage
  getToken() {
    return localStorage.getItem(this.tokenStorageKey);
  }

  // Get user data from localStorage
  getUserData() {
    const userData = localStorage.getItem(this.userStorageKey);
    return userData ? JSON.parse(userData) : null;
  }

  // Save authentication data after login
  saveAuthData(loginResponse) {
    if (loginResponse.data && loginResponse.data.token) {
      localStorage.setItem(this.tokenStorageKey, loginResponse.data.token);

      // Save user data (excluding token for security)
      const userData = { ...loginResponse.data };
      delete userData.token; // Remove token from user data storage
      localStorage.setItem(this.userStorageKey, JSON.stringify(userData));

      return true;
    }
    return false;
  }

  // Clear authentication data on logout
  clearAuthData() {
    localStorage.removeItem(this.tokenStorageKey);
    localStorage.removeItem(this.userStorageKey);

    if (this.authFunctions && this.authFunctions.logout) {
      this.authFunctions.logout();
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  }

  // Handle API response errors
  async handleResponseError(error) {
    if (!error.response) {
      console.error('Network error:', error);
      return Promise.reject(error);
    }

    const { status } = error.response;

    switch (status) {
      case 401:
        // Unauthorized - token might be invalid or user needs to login
        console.warn('401 Unauthorized - Token invalid or expired');
        this.handleUnauthorized();
        break;

      case 403:
        // Forbidden - user doesn't have permission
        console.warn('403 Forbidden - Insufficient permissions');
        // Optional: redirect to dashboard or show message
        break;

      case 404:
        // Not found
        console.warn('404 Not Found');
        break;

      default:
        console.error('API Error:', error);
    }

    return Promise.reject(error);
  }

  // Handle 401 Unauthorized responses
  async handleUnauthorized() {
    console.log('Token is invalid or expired. Redirecting to login...');

    // Clear stored auth data
    this.clearAuthData();

    // Redirect to login page
    this.redirectToLogin();
  }

  // Redirect to login page
  redirectToLogin() {
    // Preserve any return URL if needed
    const currentPath = window.location.pathname + window.location.search;
    if (currentPath !== '/login' && currentPath !== '/') {
      localStorage.setItem('return_url', currentPath);
    }

    // Redirect to login page
    window.location.href = '/login';
  }

  // Create axios interceptor configuration
  createAxiosInterceptor(axiosInstance) {
    // Request interceptor - add token to headers
    axiosInstance.interceptors.request.use(
      (config) => {
        const token = this.getToken();

        if (token) {
          config.headers.Authorization = `Token ${token}`;
          // Alternative if Django expects different header format:
          // config.headers.Authorization = `Bearer ${token}`;
          // config.headers['X-Auth-Token'] = token;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle errors
    axiosInstance.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        return this.handleResponseError(error);
      }
    );
  }

  // Alternative: Simple method to get headers with token
  getAuthHeaders() {
    const token = this.getToken();
    const headers = {
      'Content-Type': 'application/json',
    };

    if (token) {
      headers['Authorization'] = `Token ${token}`;
    }

    return headers;
  }
}

export const tokenInterceptor = new TokenInterceptor();
