// ==========================================
//
// Description: Sign Up Form Logic
//
// File: signupFormLogic.js
// Author: Anthony Bañon
// Created: 2025-11-22
// Last Updated: 2025-11-22
// ==========================================

import { useForm } from '../../../hooks/useForm';
import {
  validateAccountForm,
  validateAccountField,
} from '../../../validations/accountValidation';
import { useCallback, useEffect } from 'react';

// Initial form state - NOW RECEIVES personId
const getInitialFormState = (personId = '') => {
  return {
    username: '',
    password: '',
    confirmPassword: '',
    role: 'client',
    active: true,
    person: personId,
  };
};

// Default touched fields - ADDED confirmPassword
const defaultTouchedState = {
  username: false,
  password: false,
  confirmPassword: false,
  role: false,
  active: false,
  person: false,
};

// Custom validation for confirm password
const validateConfirmPassword = (confirmPassword, formData) => {
  if (!confirmPassword) return 'Please confirm your password';
  if (confirmPassword !== formData.password) return 'Passwords do not match';
  return null;
};

// Enhanced form validation for signup
const validateSignupForm = (formData) => {
  // First validate basic account fields
  const accountValidation = validateAccountForm(formData, false);

  // Then validate confirm password
  const confirmPasswordError = validateConfirmPassword(
    formData.confirmPassword,
    formData
  );
  // Finally validate person reference
  const personError = !formData.person ? 'Person reference is required' : null;

  return {
    errors: {
      ...accountValidation.errors,
      ...(confirmPasswordError && { confirmPassword: confirmPasswordError }),
      ...(personError && { person: personError }),
    },
    isValid: accountValidation.isValid && !confirmPasswordError && !personError,
  };
};

// Enhanced field validation for signup
const validateSignupField = (fieldName, value, formData) => {
  // Handle confirm password separately
  if (fieldName === 'confirmPassword') {
    return validateConfirmPassword(value, formData);
  }

  // Use existing account validation for other fields
  return validateAccountField(fieldName, value, { isPartialUpdate: false });
};

// Signup form logic - NOW ACCEPTS personId
export const signupFormLogic = (personId = '') => {
  // Use generic form hook with custom validation and initial personId
  const form = useForm(getInitialFormState(personId), {
    validateForm: (formData) => validateSignupForm(formData),
    validateField: (fieldName, value) =>
      validateSignupField(fieldName, value, form.formData),
    defaultTouched: defaultTouchedState,
  });
  // Sync personId prop with form state
  useEffect(() => {
    if (personId && form.formData.person !== personId) {
      form.updateField('person', personId);
    }
  }, [personId, form.updateField, form.formData.person]);

  // Enhanced canSubmit check
  const canSubmit = Boolean(
    !form.isSubmitting &&
      form.formData.username?.trim() &&
      form.formData.password &&
      form.formData.confirmPassword &&
      form.formData.person && // personId
      form.formData.password === form.formData.confirmPassword &&
      Object.values(form.errors).every((error) => !error)
  );

  // Create event handlers for form fields
  const createFieldHandlers = useCallback(
    (fieldName) => ({
      onChange: (event) => form.updateField(fieldName, event.target.value),
      onBlur: () => form.setFieldTouched(fieldName),
    }),
    [form.updateField, form.setFieldTouched]
  );

  return {
    // Form state
    formData: form.formData,
    errors: form.errors,
    touched: form.touched,
    isSubmitting: form.isSubmitting,

    // Form actions
    updateField: form.updateField,
    validateForm: form.validateForm,
    setIsSubmitting: form.setIsSubmitting,
    resetForm: form.resetForm,

    // Business logic
    canSubmit,
    createFieldHandlers,
  };
};
