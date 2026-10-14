// ==========================================
//
// Description: Use Person Form
//
// File: usePersonForm.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

import { useState, useCallback } from 'react';
import {
  validatePersonForm,
  validatePersonField,
} from '../validations/personValidation.js';

export const usePersonForm = (initialState = {}) => {
  // Form state
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    dni: '',
    email: '',
    ...initialState,
  });
  // Validation state
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Real-time field validation
  const validateField = useCallback((fieldName, value) => {
    // Validate single field
    const error = validatePersonField(fieldName, value);
    // Update errors state
    setErrors((prev) => ({
      // Keep existing errors and update only the error of the current field
      ...prev,
      [fieldName]: error,
    }));
    return error;
  }, []);

  // Update field with validation
  const updateField = useCallback(
    (fieldName, value) => {
      setFormData((prev) => ({
        ...prev,
        [fieldName]: value,
      }));

      // Validate only if field was touched
      if (touched[fieldName]) {
        validateField(fieldName, value);
      }
    },
    [touched, validateField]
  );

  // Mark field as touched
  const setFieldTouched = useCallback(
    (fieldName) => {
      setTouched((prev) => ({
        ...prev,
        [fieldName]: true,
      }));
      // Validate when field loses focus
      validateField(fieldName, formData[fieldName]);
    },
    [formData, validateField]
  );

  // Form-wide validation
  const validateForm = useCallback(() => {
    const { errors: newErrors, isValid } = validatePersonForm(formData);
    setErrors(newErrors);
    // Mark all fields as touched to show all errors
    setTouched({
      firstName: true,
      lastName: true,
      dni: true,
      email: true,
    });
    return isValid;
  }, [formData]);

  // Reset form
  const resetForm = useCallback(() => {
    setFormData(initialState);
    setErrors({});
    setTouched({});
  }, [initialState]);

  return {
    formData,
    errors,
    touched,
    isSubmitting,
    updateField,
    setFieldTouched,
    validateForm,
    validateField,
    setIsSubmitting,
    resetForm,
  };
};
