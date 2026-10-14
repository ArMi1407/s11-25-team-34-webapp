// ==========================================
// Description: Generic Form Hook
// File: useForm.js
// ==========================================

import { useState, useCallback } from 'react';

export const useForm = (initialState = {}, validationConfig = {}) => {
  const {
    validateForm: externalValidateForm,
    validateField: externalValidateField,
    defaultTouched = {},
  } = validationConfig;

  // Form state
  const [formData, setFormData] = useState(initialState);
  // Validation state
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState(defaultTouched);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Real-time field validation
  const validateField = useCallback(
    (fieldName, value) => {
      if (!externalValidateField) return null;

      const error = externalValidateField(fieldName, value);
      setErrors((prev) => ({
        ...prev,
        [fieldName]: error,
      }));
      return error;
    },
    [externalValidateField]
  );

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

  // Update multiple fields at once
  const updateFields = useCallback((fields) => {
    setFormData((prev) => ({
      ...prev,
      ...fields,
    }));
  }, []);

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

  // Mark multiple fields as touched
  const setFieldsTouched = useCallback((fieldNames) => {
    const newTouched = fieldNames.reduce((acc, fieldName) => {
      acc[fieldName] = true;
      return acc;
    }, {});

    setTouched((prev) => ({
      ...prev,
      ...newTouched,
    }));
  }, []);

  // Form-wide validation
  const validateForm = useCallback(() => {
    if (!externalValidateForm) return true;

    const { errors: newErrors, isValid } = externalValidateForm(formData);
    setErrors(newErrors);

    // Mark all fields as touched to show all errors
    const allFieldsTouched = Object.keys(formData).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});

    setTouched(allFieldsTouched);
    return isValid;
  }, [formData, externalValidateForm]);

  // Reset form
  const resetForm = useCallback(() => {
    setFormData(initialState);
    setErrors({});
    setTouched(defaultTouched);
  }, [initialState, defaultTouched]);

  // Set form data (useful for editing)
  const setForm = useCallback((newData) => {
    setFormData(newData);
  }, []);

  return {
    // State
    formData,
    errors,
    touched,
    isSubmitting,

    // Actions
    updateField,
    updateFields,
    setFieldTouched,
    setFieldsTouched,
    validateForm,
    validateField,
    setIsSubmitting,
    resetForm,
    setForm,
  };
};
