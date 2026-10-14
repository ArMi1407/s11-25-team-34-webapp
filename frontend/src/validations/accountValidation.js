// ==========================================
//
// Description: Account Validation (User and Brand Registration)
//
// File: accountValidation.js
// Author: [Tu Nombre]
// Created: 2025-11-29
// Last Updated: 2025-11-29
// ==========================================

// Regular expressions (consistentes con backend Django)
const USERNAME_REGEX = /^[a-zA-Z0-9._]{2,30}$/;
const EMAIL_REGEX = /^[\w.-]{1,64}@[\w.-]+\.[a-zA-Z]{2,63}$/;
const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñ'\s]{2,50}$/;
const PHONE_REGEX = /^[\d\s\+\-\(\)]{10,20}$/;
const BRAND_NAME_REGEX = /^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s\-\&\.]{2,100}$/;

// Funciones de validación individuales - ESTANDARIZADAS A NULL

// User validation functions
export const validateUsername = (username) => {
  if (!username?.trim()) return 'Username is required';
  if (username.length < 2 || username.length > 30)
    return 'Username must be 2-30 characters';
  if (!USERNAME_REGEX.test(username))
    return 'Username may only contain letters, numbers, dots, and underscores';
  return null;
};

export const validateEmail = (email) => {
  if (!email?.trim()) return 'Email is required';
  if (email.length < 5 || email.length > 100)
    return 'Email must be 5-100 characters';
  if (!EMAIL_REGEX.test(email)) return 'Invalid email address format';
  return null;
};

export const validatePassword = (password) => {
  if (!password) return 'Password is required';
  if (password.length < 6) return 'Password must be at least 6 characters';
  if (password.length > 255) return 'Password cannot exceed 255 characters';
  return null;
};

export const validatePasswordConfirm = (password, passwordConfirm) => {
  if (!passwordConfirm) return 'Password confirmation is required';
  if (password !== passwordConfirm) return 'Passwords do not match';
  return null;
};

export const validateFirstName = (firstName) => {
  if (!firstName?.trim()) return 'First name is required';
  if (firstName.length < 2 || firstName.length > 50)
    return 'First name must be 2-50 characters';
  if (!NAME_REGEX.test(firstName))
    return 'First name contains invalid characters';
  return null;
};

export const validateLastName = (lastName) => {
  if (!lastName?.trim()) return 'Last name is required';
  if (lastName.length < 2 || lastName.length > 50)
    return 'Last name must be 2-50 characters';
  if (!NAME_REGEX.test(lastName))
    return 'Last name contains invalid characters';
  return null;
};

export const validatePhone = (phone, isRequired = true) => {
  if (isRequired && !phone?.trim()) return 'Phone number is required';
  if (phone && phone.trim() && !PHONE_REGEX.test(phone.trim()))
    return 'Invalid phone number format';
  return null;
};

// Brand-specific validation functions
export const validateBrandName = (brandName, isRequired = true) => {
  if (isRequired && !brandName?.trim()) return 'Brand name is required';
  if (brandName && brandName.trim()) {
    if (brandName.length < 2 || brandName.length > 100)
      return 'Brand name must be 2-100 characters';
    if (!BRAND_NAME_REGEX.test(brandName))
      return 'Brand name contains invalid characters';
  }
  return null;
};

export const validateSustainabilityStory = (story) => {
  // La sustainability_story es opcional en el modelo Django
  if (story && story.length > 5000)
    return 'Sustainability story cannot exceed 5000 characters';
  return null;
};

export const validateIsBrandManager = (isBrandManager, isRequired = false) => {
  if (isRequired && (isBrandManager === undefined || isBrandManager === null))
    return 'Brand manager status is required';
  if (
    isBrandManager !== undefined &&
    isBrandManager !== null &&
    typeof isBrandManager !== 'boolean'
  )
    return 'Brand manager status must be true or false';
  return null;
};

// Helper para validación condicional
const validateIfPresent = (value, validator, isRequired = false) => {
  if (value === undefined && !isRequired) return null;
  return validator(value, isRequired);
};

// Complete form validation for User Registration (Regular User)
export const validateUserRegistration = (formData, isPartialUpdate = false) => {
  const errors = {};

  if (!isPartialUpdate) {
    // Validación completa para creación de usuario regular
    errors.username = validateUsername(formData.username);
    errors.email = validateEmail(formData.email);
    errors.password = validatePassword(formData.password);
    errors.password_confirm = validatePasswordConfirm(
      formData.password,
      formData.password_confirm
    );
    errors.first_name = validateFirstName(formData.first_name);
    errors.last_name = validateLastName(formData.last_name);
    errors.phone = validatePhone(formData.phone, false); // Phone es opcional en Django
    errors.is_brand_manager = validateIsBrandManager(
      formData.is_brand_manager || false,
      false
    );
  } else {
    // Validación parcial para actualización
    errors.username = validateIfPresent(formData.username, validateUsername);
    errors.email = validateIfPresent(formData.email, validateEmail);
    errors.password = validateIfPresent(formData.password, validatePassword);

    // Validación condicional de password_confirm solo si hay password
    if (
      formData.password !== undefined &&
      formData.password_confirm !== undefined
    ) {
      errors.password_confirm = validatePasswordConfirm(
        formData.password,
        formData.password_confirm
      );
    }

    errors.first_name = validateIfPresent(
      formData.first_name,
      validateFirstName
    );
    errors.last_name = validateIfPresent(formData.last_name, validateLastName);
    errors.phone = validateIfPresent(formData.phone, (phone) =>
      validatePhone(phone, false)
    );
    errors.is_brand_manager = validateIfPresent(
      formData.is_brand_manager,
      (value) => validateIsBrandManager(value, false)
    );

    // Verificar que al menos un campo esté presente en partial update
    const hasFields = Object.keys(formData).some(
      (key) => formData[key] !== undefined && formData[key] !== null
    );

    if (!hasFields) {
      errors._general = 'At least one field must be provided for update';
    }
  }

  // Filtrar solo errores reales (no null)
  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== null)
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

// Complete form validation for Brand Registration
export const validateBrandRegistration = (
  formData,
  isPartialUpdate = false
) => {
  const errors = {};

  // Primero validamos todos los campos de usuario
  const userValidation = validateUserRegistration(formData, isPartialUpdate);
  Object.assign(errors, userValidation.errors);

  // Luego agregamos validaciones específicas de brand
  if (!isPartialUpdate) {
    errors.brand_name = validateBrandName(formData.brand_name, true);
    errors.sustainability_story = validateSustainabilityStory(
      formData.sustainability_story
    );
  } else {
    errors.brand_name = validateIfPresent(formData.brand_name, (value) =>
      validateBrandName(value, false)
    );
    errors.sustainability_story = validateIfPresent(
      formData.sustainability_story,
      validateSustainabilityStory
    );
  }

  // Filtrar solo errores reales (no null)
  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== null)
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

// Individual field validation (para validación en tiempo real)
export const validateAccountField = (fieldName, value, context = {}) => {
  const {
    formType = 'user', // 'user' o 'brand'
    isPartialUpdate = false,
    password = null,
    passwordConfirm = null,
  } = context;

  const validators = {
    // Campos comunes
    username: validateUsername,
    email: validateEmail,
    password: validatePassword,
    password_confirm: (val) => validatePasswordConfirm(password, val),
    first_name: validateFirstName,
    last_name: validateLastName,
    phone: (val) => validatePhone(val, false),
    is_brand_manager: (val) => validateIsBrandManager(val, false),

    // Campos específicos de brand
    brand_name: (val) =>
      validateBrandName(val, formType === 'brand' && !isPartialUpdate),
    sustainability_story: validateSustainabilityStory,
  };

  if (!validators[fieldName]) {
    return null;
  }

  return validators[fieldName](value);
};

// Utility to check if the form has changes
export const hasAccountChanges = (originalData, currentData) => {
  return Object.keys(currentData).some((key) => {
    const currentVal = currentData[key];
    const originalVal = originalData[key];

    // Manejo robusto de comparación incluyendo null/undefined
    if (currentVal === originalVal) return false;
    if (currentVal == null && originalVal == null) return false;

    return currentVal !== originalVal;
  });
};

// Validaciones específicas para operaciones individuales
export const validateAccountUsername = (username) => {
  return validateUsername(username);
};

export const validateAccountEmail = (email) => {
  return validateEmail(email);
};

export const validateAccountPassword = (password) => {
  return validatePassword(password);
};

export const validateAccountPhone = (phone) => {
  return validatePhone(phone, false);
};

// Helper para validación en tiempo real
export const createFieldValidator = (fieldName, context = {}) => {
  return (value) => validateAccountField(fieldName, value, context);
};

// Helper para resetear errores según el tipo de formulario
export const initializeErrors = (formType = 'user') => {
  const baseErrors = {
    username: null,
    email: null,
    password: null,
    password_confirm: null,
    first_name: null,
    last_name: null,
    phone: null,
    is_brand_manager: null,
    _general: null,
  };

  if (formType === 'brand') {
    return {
      ...baseErrors,
      brand_name: null,
      sustainability_story: null,
    };
  }

  return baseErrors;
};

// Función para determinar qué validación usar basado en los datos
export const validateAccountForm = (formData, options = {}) => {
  const { isPartialUpdate = false, isBrand = false } = options;

  if (isBrand) {
    return validateBrandRegistration(formData, isPartialUpdate);
  } else {
    return validateUserRegistration(formData, isPartialUpdate);
  }
};

// Función para validar que el formulario sea para brand manager
export const validateBrandManagerForm = (formData) => {
  const errors = {};

  if (formData.is_brand_manager !== true) {
    errors.is_brand_manager = 'Must be a brand manager to register a brand';
  }

  if (!formData.brand_name?.trim()) {
    errors.brand_name = 'Brand name is required for brand managers';
  }

  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== null)
  );

  return {
    errors: filteredErrors,
    isValid: Object.keys(filteredErrors).length === 0,
  };
};
