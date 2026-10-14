// ==========================================
//
// Description: Constants file
//
// File: constants.js
// Author: Anthony Bañon
// Created: 2025-12-09
// Last Updated: 2025-12-09
// ==========================================

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
};

export const ERROR_MESSAGES = {
  UNAUTHORIZED: 'Sesión expirada. Por favor, inicie sesión nuevamente.',
  INVALID_CREDENTIALS: 'Usuario o contraseña incorrectos.',
  NETWORK_ERROR:
    'Error de conexión. Por favor, verifique su conexión a internet.',
  SERVER_ERROR: 'Error del servidor. Por favor, intente nuevamente.',
};

export const ROUTES = {
  LOGIN: '/login',
  HOME: '/',
  DASHBOARD: '/dashboard',
};

export const API_ENDPOINTS = {
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  CHANGE_PASSWORD: '/auth/change-password',
  PROFILE: '/profile',
};
