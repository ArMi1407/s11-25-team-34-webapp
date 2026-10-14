// ==========================================
//
// Description: Person Validation
//
// File: personValidation.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

// Regular expressions (consistentes con backend)
const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñ']{2,50}$/;
const DNI_REGEX = /^[0-9]{8}$/;
const EMAIL_REGEX = /^[\w.-]{1,64}@[\w.-]+\.[a-zA-Z]{2,63}$/;

// Validation functions - MEJORADO: null para éxito, string para error
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

export const validateDni = (dni) => {
  if (!dni?.trim()) return 'DNI is required';
  if (dni.length !== 8) return 'DNI must be exactly 8 digits';
  if (!DNI_REGEX.test(dni)) return 'DNI must contain only numbers (8 digits)';
  return null;
};

export const validateEmail = (email) => {
  if (!email?.trim()) return 'Email is required';
  if (email.length < 5 || email.length > 100)
    return 'Email must be 5-100 characters';
  if (!EMAIL_REGEX.test(email)) return 'Invalid email address format';
  return null;
};

export const validateIsActive = (isActive, isRequired = false) => {
  if (isRequired && (isActive === undefined || isActive === null))
    return 'Active status is required';
  if (
    isActive !== undefined &&
    isActive !== null &&
    typeof isActive !== 'boolean'
  )
    return 'Active status must be true or false';
  return null;
};

// Helper para validación condicional - MÁS ROBUSTO
const validateIfPresent = (value, validator, isRequired = false) => {
  // Para valores undefined, no validar a menos que sea requerido
  if (value === undefined && !isRequired) return null;
  return validator(value, isRequired);
};

// Complete form validation - OPTIMIZADO
export const validatePersonForm = (formData, isPartialUpdate = false) => {
  const errors = {};

  // Validación condicional basada en el contexto
  if (!isPartialUpdate) {
    // Validación completa para creación
    errors.firstName = validateFirstName(formData.firstName);
    errors.lastName = validateLastName(formData.lastName);
    // errors.dni = validateDni(formData.dni);
    errors.email = validateEmail(formData.email);
    errors.isActive = validateIsActive(formData.isActive, true);
  } else {
    // Validación parcial para actualización
    errors.firstName = validateIfPresent(formData.firstName, validateFirstName);
    errors.lastName = validateIfPresent(formData.lastName, validateLastName);
    // errors.dni = validateIfPresent(formData.dni, validateDni);
    errors.email = validateIfPresent(formData.email, validateEmail);
    errors.isActive = validateIfPresent(formData.isActive, validateIsActive);

    // Verificar que al menos un campo esté presente en partial update
    const hasFields = Object.keys(formData).some(
      (key) => formData[key] !== undefined && formData[key] !== null
    );

    if (!hasFields) {
      errors._general = 'At least one field must be provided for update';
    }
  }

  // Filtrar solo errores no nulos
  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== null)
  );

  return {
    errors: filteredErrors,
    isValid: Object.keys(filteredErrors).length === 0,
  };
};

// Validaciones específicas para operaciones individuales
export const validatePersonStatus = (isActive) => {
  return validateIsActive(isActive, true);
};

// export const validatePersonDni = (dni) => {
//   return validateDni(dni);
// };

export const validatePersonEmail = (email) => {
  return validateEmail(email);
};

// Individual field validation - MEJORADO para React forms
export const validatePersonField = (fieldName, value, context = {}) => {
  const { isPartialUpdate = false } = context;

  const validators = {
    firstName: validateFirstName,
    lastName: validateLastName,
    // dni: validateDni,
    email: validateEmail,
    isActive: (val) => validateIsActive(val, !isPartialUpdate),
  };

  const validator = validators[fieldName];
  if (!validator) return null;

  return isPartialUpdate && value === undefined ? null : validator(value);
};

// Utility to check if the form has changes - MEJORADO
export const hasFormChanges = (originalData, currentData) => {
  return Object.keys(currentData).some((key) => {
    const currentVal = currentData[key];
    const originalVal = originalData[key];

    // Manejo robusto de comparación incluyendo null/undefined
    if (currentVal === originalVal) return false;
    if (currentVal == null && originalVal == null) return false;

    return currentVal !== originalVal;
  });
};

// Helper para validación en tiempo real - NUEVO
export const createFieldValidator = (fieldName, context = {}) => {
  return (value) => validatePersonField(fieldName, value, context);
};

// Helper para resetear errores - NUEVO
export const initializeErrors = () => ({
  firstName: null,
  lastName: null,
  // dni: null,
  email: null,
  isActive: null,
  _general: null,
});
