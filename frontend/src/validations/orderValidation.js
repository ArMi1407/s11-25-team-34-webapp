// ==========================================
//
// Description: Order Validation
//
// File: orderValidation.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

// Regular expressions
const ORDER_NUMBER_REGEX = /^[A-Z0-9-_]{4,20}$/;
const ISO_REGEX = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?)?$/;
const MONGO_ID_REGEX = /^[0-9a-fA-F]{24}$/;

// Status values (SINGLE SOURCE)
const ORDER_STATUSES = ['pending', 'paid', 'shipped', 'cancelled', 'delivered'];

// Funciones de validación individuales
export const validateOrderNumber = (orderNumber) => {
  if (!orderNumber) return 'Order number is required';
  if (orderNumber.length < 4 || orderNumber.length > 20)
    return 'Order number must be 4-20 characters';
  if (!ORDER_NUMBER_REGEX.test(orderNumber))
    return 'Order number can only contain uppercase letters, numbers, hyphen, and underscore';
  return '';
};

export const validateDate = (date) => {
  if (!date) return ''; // Opcional según el backend

  // Validar formato ISO 8601
  if (!ISO_REGEX.test(date)) {
    return 'Date must be in ISO 8601 format (YYYY-MM-DD)';
  }

  // Validar que no sea fecha futura
  const inputDate = new Date(date);
  const today = new Date();
  if (inputDate > today) {
    return 'Order date cannot be in the future';
  }

  return '';
};

export const validateStatus = (status) => {
  if (!status) return 'Status is required';
  if (!ORDER_STATUSES.includes(status))
    return `Status must be one of: ${ORDER_STATUSES.join(', ')}`;
  return '';
};

export const validateAccount = (account) => {
  if (!account) return 'Account is required';
  // Validación básica de MongoDB ID (24 caracteres hex)
  if (typeof account !== 'string' || !MONGO_ID_REGEX.test(account))
    return 'Valid account ID is required';
  return '';
};

export const validateOrderIds = (orderIds) => {
  if (!orderIds || !Array.isArray(orderIds))
    return 'Order IDs must be a non-empty array';

  if (orderIds.length === 0) return 'Order IDs must be a non-empty array';

  for (const id of orderIds) {
    if (typeof id !== 'string' || !MONGO_ID_REGEX.test(id)) {
      return 'Each order ID must be valid';
    }
  }

  return '';
};

// Validación completa del formulario
export const validateOrderForm = (formData, isPartialUpdate = false) => {
  const errors = {};

  // Validaciones condicionales para actualización parcial
  if (!isPartialUpdate || formData.order_number !== undefined) {
    errors.order_number = validateOrderNumber(formData.order_number);
  }

  if (formData.date !== undefined) {
    errors.date = validateDate(formData.date);
  }

  if (!isPartialUpdate || formData.status !== undefined) {
    errors.status = validateStatus(formData.status);
  }

  if (!isPartialUpdate || formData.account !== undefined) {
    errors.account = validateAccount(formData.account);
  }

  // Para actualización parcial: validar que hay al menos un campo
  if (isPartialUpdate && Object.keys(formData).length === 0) {
    errors._general = 'At least one field must be provided for update';
  }

  // Filtrar errores vacíos y determinar si es válido
  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== '')
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

// Validaciones específicas para operaciones individuales
export const validateOrderStatus = (status) => {
  if (!status) return 'Status field is required';
  if (!ORDER_STATUSES.includes(status))
    return `Status must be one of: ${ORDER_STATUSES.join(', ')}`;
  return '';
};

export const validateBulkOrderStatus = (orderIds, status) => {
  const errors = {};

  errors.order_ids = validateOrderIds(orderIds);
  errors.status = validateOrderStatus(status);

  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== '')
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

export const validateDateRange = (startDate, endDate) => {
  const errors = {};

  if (startDate) {
    if (!ISO_REGEX.test(startDate)) {
      errors.start_date = 'Start date must be in ISO 8601 format';
    }
  }

  if (endDate) {
    if (!ISO_REGEX.test(endDate)) {
      errors.end_date = 'End date must be in ISO 8601 format';
    } else if (startDate && new Date(endDate) < new Date(startDate)) {
      errors.end_date = 'End date cannot be before start date';
    }
  }

  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== '')
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

// Validación individual de campo (útil para validación en tiempo real)
export const validateOrderField = (
  fieldName,
  value,
  isPartialUpdate = false
) => {
  const validators = {
    order_number: validateOrderNumber,
    date: validateDate,
    status: validateStatus,
    account: validateAccount,
    order_ids: validateOrderIds,
  };

  if (!validators[fieldName]) {
    return '';
  }

  return validators[fieldName](value);
};

// Utilidad para verificar si el formulario tiene cambios
export const hasOrderChanges = (originalData, currentData) => {
  return Object.keys(currentData).some((key) => {
    return currentData[key] !== originalData[key];
  });
};

// Utilidades para formateo y helpers
export const formatOrderNumber = (value) => {
  return value ? value.toUpperCase().replace(/[^A-Z0-9-_]/g, '') : '';
};

export const isValidOrderStatus = (status) => {
  return ORDER_STATUSES.includes(status);
};

export const getOrderStatusOptions = () => {
  return ORDER_STATUSES.map((status) => ({
    value: status,
    label: status.charAt(0).toUpperCase() + status.slice(1),
  }));
};
