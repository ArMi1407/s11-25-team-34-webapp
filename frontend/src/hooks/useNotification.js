// ==========================================
//
// Description: Notification
//
// File: useNotification.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

// useNotification.js
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export const useNotification = () => {
  // Configuración por defecto
  const defaultOptions = {
    position: 'top-right',
    autoClose: 3000,
    hideProgressBar: false,
    closeOnClick: true,
    pauseOnHover: true,
    draggable: true,
  };

  const showSuccess = (message, options = {}) => {
    toast.success(message, {
      ...defaultOptions,
      autoClose: 3000,
      ...options,
    });
  };

  const showError = (message, options = {}) => {
    toast.error(message, {
      ...defaultOptions,
      autoClose: 5000,
      ...options,
    });
  };

  const showWarning = (message, options = {}) => {
    toast.warn(message, {
      ...defaultOptions,
      autoClose: 4000,
      ...options,
    });
  };

  const showInfo = (message, options = {}) => {
    toast.info(message, {
      ...defaultOptions,
      autoClose: 3000,
      ...options,
    });
  };

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
};
