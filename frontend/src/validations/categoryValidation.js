// ==========================================
//
// Description: Category Validation
//
// File: categoryValidation.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

// Regular expressions
const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 .,'\-]{2,150}$/;

// Funciones de validación individuales
export const validateCategoryName = (name) => {
  if (!name) return 'Category name is required';
  if (name.length < 2 || name.length > 150)
    return 'Name must be 2-150 characters';
  if (!NAME_REGEX.test(name))
    return 'Category name contains invalid characters';
  return '';
};

export const validateDescription = (description) => {
  if (!description) return ''; // Opcional
  if (description.length < 2 || description.length > 2000)
    return 'Description must be 2-2000 characters';
  return '';
};

export const validateIsActive = (isActive) => {
  if (isActive === undefined || isActive === null) return '';
  if (typeof isActive !== 'boolean')
    return 'Active status must be true or false';
  return '';
};

// Validación completa del formulario
export const validateCategoryForm = (formData, isPartialUpdate = false) => {
  const errors = {};

  if (!isPartialUpdate || formData.name !== undefined) {
    errors.name = validateCategoryName(formData.name);
  }

  if (formData.description !== undefined) {
    errors.description = validateDescription(formData.description);
  }

  if (formData.is_active !== undefined) {
    errors.is_active = validateIsActive(formData.is_active);
  }

  // Para actualización parcial: validar que hay al menos un campo
  if (isPartialUpdate && Object.keys(formData).length === 0) {
    errors._general = 'At least one field must be provided for update';
  }

  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== '')
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

// Validaciones específicas para operaciones individuales
export const validateCategoryStatus = (isActive) => {
  if (isActive === undefined || isActive === null)
    return 'is_active field is required';
  if (typeof isActive !== 'boolean') return 'is_active must be true or false';
  return '';
};

// Validación individual de campo
export const validateCategoryField = (
  fieldName,
  value,
  isPartialUpdate = false
) => {
  const validators = {
    name: validateCategoryName,
    description: validateDescription,
    is_active: validateIsActive,
  };

  if (!validators[fieldName]) {
    return '';
  }

  return validators[fieldName](value);
};

// Utilidad para verificar si el formulario tiene cambios
export const hasCategoryChanges = (originalData, currentData) => {
  return Object.keys(currentData).some((key) => {
    return currentData[key] !== originalData[key];
  });
};

// Utilidad para formatear nombre de categoría
export const formatCategoryName = (name) => {
  return name ? name.trim() : '';
};
