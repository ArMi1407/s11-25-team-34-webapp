// ==========================================
//
// Description: Login Page Business Logic
//
// File: loginPageLogic.js
// Author: Anthony Bañon
// Created: 2025-11-22
// Last Updated: 2025-11-22
// ==========================================

import { useAuth } from '../../contexts/AuthContext';
import { useNotification } from '../../hooks/useNotification';
import { useNavigate } from 'react-router-dom';

// Page business logic for login page
export const loginPageLogic = () => {
  const { login, loading } = useAuth();
  const { showError } = useNotification();
  const navigate = useNavigate();
  // Handle user login
  const handleLogin = async (formData) => {
    try {
      // Attempt login
      const result = await login(formData.username, formData.password);
      // On successful login, navigate to home
      if (result.success) {
        navigate('/');
      } else {
        showError(result.error || 'Login failed. Please try again.');
      }
    } catch (error) {
      console.error('Login error:', error);
      showError(error.message || 'An unexpected error occurred.');
    }
  };

  return {
    handleLogin,
    isLoading: loading,
  };
};
