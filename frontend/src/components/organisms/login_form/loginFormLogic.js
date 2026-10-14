// ==========================================
//
// Description: Login Form Business Logic
//
// File: loginFormLogic.js
// Author: Anthony Bañon
// Created: 2025-11-22
// Last Updated: 2025-11-22
// ==========================================

import { useForm } from '../../../hooks/useForm';
import {
  validateLoginForm,
  validateAuthField,
} from '../../../validations/authValidation';
import { useCallback } from 'react';

// Initial form state
const initialFormState = {
  username: '',
  password: '',
};

// Default touched fields
const defaultTouchedState = {
  username: false,
  password: false,
};
// Login form logic
export const loginFormLogic = () => {
  // Use generic form hook
  const form = useForm(initialFormState, {
    validateForm: validateLoginForm, // Use login-specific form validation
    validateField: validateAuthField,
    defaultTouched: defaultTouchedState, // Set default touched fields
  });

  // Check if form can be submitted
  const canSubmit = Boolean(
    !form.isSubmitting &&
      form.formData.username?.trim() &&
      form.formData.password &&
      Object.values(form.errors).every((error) => !error) // Only truthy mistakes
  );
  // Create event handlers for form fields
  const createFieldHandlers = useCallback(
    (fieldName) => ({
      onChange: (event) => form.updateField(fieldName, event.target.value),
      onBlur: () => form.setFieldTouched(fieldName),
    }),
    [form.updateField, form.setFieldTouched, form.formData] // Add dependencies
  );

  return {
    // Form state
    formData: form.formData,
    errors: form.errors,
    touched: form.touched,
    isSubmitting: form.isSubmitting,

    // Form actions
    validateForm: form.validateForm,
    setIsSubmitting: form.setIsSubmitting,
    resetForm: form.resetForm,

    // Business logic
    canSubmit,
    createFieldHandlers,
  };
};
