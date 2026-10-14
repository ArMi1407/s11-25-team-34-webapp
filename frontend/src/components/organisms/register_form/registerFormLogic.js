// ==========================================
//
// Description: Register Form Business Logic
//
// File: registerFormLogic.js
// Author: Anthony Bañon
// Created: 2025-11-29
// Last Updated: 2025-11-29
// ==========================================

import { useForm } from '../../../hooks/useForm';
import {
  validateUserRegistration,
  validateAccountField,
  initializeErrors,
} from '../../../validations/accountValidation';
import { useCallback } from 'react';

// Initial form state para usuario regular
const initialFormState = {
  username: '',
  email: '',
  password: '',
  password_confirm: '',
  first_name: '',
  last_name: '',
  phone: '',
  is_brand_manager: false,
};

// Campos específicos para brand (opcional, se puede activar después)
const brandFormState = {
  ...initialFormState,
  brand_name: '',
  sustainability_story: '',
  is_brand_manager: true,
};

// Default touched fields
const defaultTouchedState = {
  username: false,
  email: false,
  password: false,
  password_confirm: false,
  first_name: false,
  last_name: false,
  phone: false,
  is_brand_manager: false,
  // brand_name: false,
  // sustainability_story: false,
};

// Register form logic
export const registerFormLogic = (options = {}) => {
  const { isBrandRegistration = false } = options;

  // Usar el estado inicial correspondiente
  const initialState = isBrandRegistration ? brandFormState : initialFormState;
  const initialTouched = isBrandRegistration
    ? { ...defaultTouchedState, brand_name: false, sustainability_story: false }
    : defaultTouchedState;

  // Use generic form hook
  const form = useForm(initialState, {
    validateForm: (formData) =>
      isBrandRegistration
        ? validateBrandRegistration(formData, false)
        : validateUserRegistration(formData, false),
    validateField: (fieldName, value, context = {}) => {
      const validationContext = {
        ...context,
        formType: isBrandRegistration ? 'brand' : 'user',
        isPartialUpdate: false,
        // Pasar passwords para validación de confirmación
        password:
          fieldName === 'password_confirm' ? form.formData.password : null,
        passwordConfirm:
          fieldName === 'password' ? form.formData.password_confirm : null,
      };

      return validateAccountField(fieldName, value, validationContext);
    },
    defaultTouched: initialTouched,
  });

  // Check if form can be submitted
  const canSubmit = Boolean(
    !form.isSubmitting &&
      form.formData.username?.trim() &&
      form.formData.email?.trim() &&
      form.formData.password?.trim() &&
      form.formData.password_confirm?.trim() &&
      form.formData.first_name?.trim() &&
      form.formData.last_name?.trim() &&
      // Para brand, también requerir brand_name
      (!isBrandRegistration || form.formData.brand_name?.trim()) &&
      Object.values(form.errors).every((error) => !error)
  );

  // Create event handlers for form fields
  const createFieldHandlers = useCallback(
    (fieldName) => ({
      onChange: (event) => {
        const value =
          event.target.type === 'checkbox'
            ? event.target.checked
            : event.target.value;
        form.updateField(fieldName, value);

        // Validación especial para password matching
        if (fieldName === 'password') {
          // Si hay password_confirm, validarlo también
          if (form.formData.password_confirm) {
            setTimeout(() => form.validateField('password_confirm'), 0);
          }
        } else if (fieldName === 'password_confirm') {
          // Si se está escribiendo el confirm, también validar password
          if (form.formData.password) {
            setTimeout(() => form.validateField('password'), 0);
          }
        }
      },
      onBlur: () => form.setFieldTouched(fieldName),
    }),
    [form.updateField, form.setFieldTouched, form.validateField, form.formData]
  );

  // Función para resetear form específico
  const resetForm = useCallback(() => {
    form.resetForm();
    form.setTouched(initializeErrors(isBrandRegistration ? 'brand' : 'user'));
  }, [form.resetForm, form.setTouched, isBrandRegistration]);

  return {
    // Form state
    formData: form.formData,
    errors: form.errors,
    touched: form.touched,
    isSubmitting: form.isSubmitting,
    isValid: form.isValid,

    // Form actions
    validateForm: form.validateForm,
    setIsSubmitting: form.setIsSubmitting,
    resetForm,

    // Form update methods
    updateField: form.updateField,
    setFieldTouched: form.setFieldTouched,
    setTouched: form.setTouched,

    // Business logic
    canSubmit,
    createFieldHandlers,
    isBrandRegistration,
  };
};
