// ==========================================
//
// Description: Register Page Business Logic
//
// File: registerPageLogic.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

import { useNavigate } from 'react-router-dom';
import { useNotification } from '../../hooks/useNotification';
import { accountService } from '../../services/accounts/accountService';

// Page business logic for register page
export const registerPageLogic = () => {
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotification();

  // Handle user registration
  const handleRegister = async (formData) => {
    try {
      // Call service to create person
      const createdPerson = await accountService.registerUser({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.password_confirm,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
      });

      showSuccess('Account created successfully!');

      // Redirect after success
      setTimeout(() => {
        navigate('/', {
          state: {
            message: 'Personal data saved. Now create your login credentials.',
            userId: createdPerson.data.id, // Pass userId to signup page
            userData: createdPerson.data,
          },
        });
      }, 1500);

      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);

      // Handle specific error cases
      if (error.response?.status === 409) {
        showError('Email or DNI already exists');
      } else if (error.response?.status === 401) {
        showError('Session expired. Please try again.');
      } else if (error.response?.status === 400) {
        showError('Invalid data. Please check your information.');
      } else {
        showError('Registration failed. Please try again.');
      }

      return { success: false, error: error.message };
    }
  };

  return {
    handleRegister,
    isLoading: false, // No tenemos loading state específico de página, solo del form
  };
};
