// ==========================================
//
// Description: Product Validation
//
// File: productValidation.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

// Regular expressions
const SKU_REGEX = /^[A-Z0-9-]{3,20}$/;
const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9 .,'\-]{2,150}$/;

// Funciones de validación individuales
export const validateSku = (sku) => {
  if (!sku) return 'SKU is required';
  if (sku.length < 3 || sku.length > 20) return 'SKU must be 3-20 characters';
  if (!SKU_REGEX.test(sku))
    return 'SKU can only contain uppercase letters, numbers, and hyphen';
  return '';
};

export const validateName = (name) => {
  if (!name) return 'Product name is required';
  if (name.length < 2 || name.length > 150)
    return 'Name must be 2-150 characters';
  if (!NAME_REGEX.test(name)) return 'Product name contains invalid characters';
  return '';
};

export const validateDescription = (description) => {
  if (!description) return ''; // Opcional
  if (description.length < 2 || description.length > 2000)
    return 'Description must be 2-2000 characters';
  return '';
};

export const validatePrice = (price) => {
  if (!price && price !== 0) return 'Price is required';
  const numPrice = parseFloat(price);
  if (isNaN(numPrice)) return 'Price must be a valid number';
  if (numPrice < 0.01) return 'Price must be greater than 0';
  return '';
};

export const validateStock = (stock) => {
  if (!stock && stock !== 0) return 'Stock is required';
  const numStock = parseInt(stock);
  if (isNaN(numStock)) return 'Stock must be a valid integer';
  if (numStock < 0) return 'Stock must be a non-negative integer';
  return '';
};

export const validateIsActive = (isActive) => {
  if (isActive === undefined || isActive === null) return '';
  if (typeof isActive !== 'boolean')
    return 'Active status must be true or false';
  return '';
};

export const validateCategory = (category) => {
  if (!category) return 'Category is required';
  if (typeof category !== 'string' || !/^[0-9a-fA-F]{24}$/.test(category))
    return 'Valid category ID is required';
  return '';
};

export const validateQuantity = (quantity) => {
  if (!quantity && quantity !== 0) return 'Quantity is required';
  const numQuantity = parseInt(quantity);
  if (isNaN(numQuantity)) return 'Quantity must be an integer';
  return '';
};

// Validación completa del formulario
export const validateProductForm = (formData, isPartialUpdate = false) => {
  const errors = {};

  if (!isPartialUpdate || formData.sku !== undefined) {
    errors.sku = validateSku(formData.sku);
  }

  if (!isPartialUpdate || formData.name !== undefined) {
    errors.name = validateName(formData.name);
  }

  if (formData.description !== undefined) {
    errors.description = validateDescription(formData.description);
  }

  if (!isPartialUpdate || formData.price !== undefined) {
    errors.price = validatePrice(formData.price);
  }

  if (!isPartialUpdate || formData.stock !== undefined) {
    errors.stock = validateStock(formData.stock);
  }

  if (formData.is_active !== undefined) {
    errors.is_active = validateIsActive(formData.is_active);
  }

  if (!isPartialUpdate || formData.category !== undefined) {
    errors.category = validateCategory(formData.category);
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
export const validateProductStatus = (isActive) => {
  if (isActive === undefined || isActive === null)
    return 'is_active field is required';
  if (typeof isActive !== 'boolean') return 'is_active must be true or false';
  return '';
};

export const validateStockUpdate = (quantity) => {
  return validateQuantity(quantity);
};

export const validateBulkProductUpdate = (products) => {
  const errors = {};

  if (!products || !Array.isArray(products)) {
    errors._general = 'Request body must be an array';
    return { errors, isValid: false };
  }

  const itemErrors = [];

  products.forEach((product, index) => {
    const itemError = {};

    if (product.sku !== undefined) {
      itemError.sku = validateSku(product.sku);
    }

    if (product.price !== undefined) {
      itemError.price = validatePrice(product.price);
    }

    if (product.stock !== undefined) {
      itemError.stock = validateStock(product.stock);
    }

    const filteredItemErrors = Object.fromEntries(
      Object.entries(itemError).filter(([_, value]) => value !== '')
    );

    if (Object.keys(filteredItemErrors).length > 0) {
      itemErrors[index] = filteredItemErrors;
    }
  });

  if (itemErrors.length > 0) {
    errors.items = itemErrors;
  }

  const isValid = Object.keys(errors).length === 0;
  return { errors, isValid };
};

// Validación individual de campo
export const validateProductField = (
  fieldName,
  value,
  isPartialUpdate = false
) => {
  const validators = {
    sku: validateSku,
    name: validateName,
    description: validateDescription,
    price: validatePrice,
    stock: validateStock,
    is_active: validateIsActive,
    category: validateCategory,
  };

  if (!validators[fieldName]) {
    return '';
  }

  return validators[fieldName](value);
};

// Utilidades para formateo
export const formatSku = (value) => {
  return value ? value.toUpperCase().replace(/[^A-Z0-9-]/g, '') : '';
};

// Utilidad para verificar si el formulario tiene cambios
export const hasProductChanges = (originalData, currentData) => {
  return Object.keys(currentData).some((key) => {
    return currentData[key] !== originalData[key];
  });
};

// Utilidad para calcular valores
export const calculateTotalValue = (stock, price) => {
  const stockNum = parseInt(stock) || 0;
  const priceNum = parseFloat(price) || 0;
  return (stockNum * priceNum).toFixed(2);
};
