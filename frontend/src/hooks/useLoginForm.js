// ==========================================
//
// Description: Use Login Form Hook
//
// File: useLoginForm.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

import { useState, useCallback } from 'react';
import {
  validateLoginForm,
  validateAuthField,
} from '../validations/authValidation';

export const useLoginForm = (initialState = {}) => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    ...initialState,
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  const updateField = useCallback(
    (fieldName, value) => {
      setFormData((prev) => ({
        ...prev,
        [fieldName]: value,
      }));

      // Real-time validation for touched fields
      if (touched[fieldName]) {
        const error = validateAuthField(fieldName, value, formData);
        setErrors((prev) => ({
          ...prev,
          [fieldName]: error,
        }));
      }
    },
    [touched, formData]
  );

  const setFieldTouched = useCallback(
    (fieldName) => {
      setTouched((prev) => ({
        ...prev,
        [fieldName]: true,
      }));
      // Validate on blur
      const error = validateAuthField(fieldName, formData[fieldName], formData);
      setErrors((prev) => ({
        ...prev,
        [fieldName]: error,
      }));
    },
    [formData]
  );

  const validateForm = useCallback(() => {
    const { errors: newErrors, isValid } = validateLoginForm(formData);
    setErrors(newErrors);
    // Mark all fields as touched to show all errors
    setTouched({
      username: true,
      password: true,
    });
    return isValid;
  }, [formData]);

  const resetForm = useCallback(() => {
    setFormData({ username: '', password: '' });
    setErrors({});
    setTouched({});
  }, []);

  return {
    formData,
    errors,
    touched,
    updateField,
    setFieldTouched,
    validateForm,
    resetForm,
  };
};
