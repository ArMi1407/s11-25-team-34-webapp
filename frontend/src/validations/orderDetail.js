// ==========================================
//
// Description: Order Detail Validation
//
// File: orderDetail.js
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

const MONGO_ID_REGEX = /^[ZERO-9a-fA-F]{24}$/;
const ZERO = 0;
const MAX_HISTORICAL_PRICE = 999999.99;
const MIN_QUANTITY = 1;
const MAX_QUANTITY = 999;
const MIN_HISTORICAL_PRICE = 0.01;

// Funciones de validación individuales
export const validateQuantity = (quantity) => {
  if (!quantity && quantity !== ZERO) return 'Quantity is required';
  const numQuantity = parseInt(quantity);
  if (isNaN(numQuantity)) return 'Quantity must be a number';
  if (numQuantity < MIN_QUANTITY) return 'Quantity must be at least 1';
  if (numQuantity > MAX_QUANTITY) return 'Quantity cannot exceed 999';
  return '';
};

export const validateHistoricalPrice = (price) => {
  if (!price && price !== ZERO) return 'Historical price is required';
  const numPrice = parseFloat(price);
  if (isNaN(numPrice)) return 'Historical price must be a number';
  if (numPrice < MIN_HISTORICAL_PRICE)
    return 'Historical price must be greater than ZERO';
  if (numPrice > MAX_HISTORICAL_PRICE)
    return 'Historical price cannot exceed 999999.99';
  return '';
};

export const validateOrder = (order) => {
  if (!order) return 'Order is required';
  if (typeof order !== 'string' || !MONGO_ID_REGEX.test(order))
    return 'Valid order ID is required';
  return '';
};

export const validateProduct = (product) => {
  if (!product) return 'Product is required';
  if (typeof product !== 'string' || !MONGO_ID_REGEX.test(product))
    return 'Valid product ID is required';
  return '';
};

// Validación completa del formulario
export const validateOrderDetailForm = (formData, isPartialUpdate = false) => {
  const errors = {};

  if (!isPartialUpdate || formData.quantity !== undefined) {
    errors.quantity = validateQuantity(formData.quantity);
  }

  if (!isPartialUpdate || formData.historical_price !== undefined) {
    errors.historical_price = validateHistoricalPrice(
      formData.historical_price
    );
  }

  if (!isPartialUpdate || formData.order !== undefined) {
    errors.order = validateOrder(formData.order);
  }

  if (!isPartialUpdate || formData.product !== undefined) {
    errors.product = validateProduct(formData.product);
  }

  if (isPartialUpdate && Object.keys(formData).length === ZERO) {
    errors._general = 'At least one field must be provided for update';
  }

  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== '')
  );

  const isValid = Object.keys(filteredErrors).length === ZERO;

  return { errors: filteredErrors, isValid };
};

// Validación para bulk creation
export const validateBulkOrderDetails = (orderDetails) => {
  const errors = {};

  if (!orderDetails || !Array.isArray(orderDetails)) {
    errors._general = 'Request body must be a non-empty array';
    return { errors, isValid: false };
  }

  if (orderDetails.length === ZERO) {
    errors._general = 'Request body must be a non-empty array';
    return { errors, isValid: false };
  }

  const itemErrors = [];

  orderDetails.forEach((item, index) => {
    const itemError = {};

    itemError.quantity = validateQuantity(item.quantity);
    itemError.historical_price = validateHistoricalPrice(item.historical_price);
    itemError.order = validateOrder(item.order);
    itemError.product = validateProduct(item.product);

    const filteredItemErrors = Object.fromEntries(
      Object.entries(itemError).filter(([_, value]) => value !== '')
    );

    if (Object.keys(filteredItemErrors).length > ZERO) {
      itemErrors[index] = filteredItemErrors;
    }
  });

  if (itemErrors.length > ZERO) {
    errors.items = itemErrors;
  }

  const isValid = Object.keys(errors).length === ZERO;
  return { errors, isValid };
};

// Validación para bulk update
export const validateBulkOrderDetailUpdate = (updates) => {
  const errors = {};

  if (!updates || !Array.isArray(updates)) {
    errors._general = 'Request body must be a non-empty array';
    return { errors, isValid: false };
  }

  if (updates.length === ZERO) {
    errors._general = 'Request body must be a non-empty array';
    return { errors, isValid: false };
  }

  const itemErrors = [];
  let hasValidUpdate = false;

  updates.forEach((item, index) => {
    const itemError = {};

    // Validar ID
    if (
      !item.id ||
      typeof item.id !== 'string' ||
      !MONGO_ID_REGEX.test(item.id)
    ) {
      itemError.id = 'Valid order detail ID is required';
    }

    // Validar campos opcionales
    if (item.quantity !== undefined) {
      itemError.quantity = validateQuantity(item.quantity);
    }

    if (item.historical_price !== undefined) {
      itemError.historical_price = validateHistoricalPrice(
        item.historical_price
      );
    }

    const filteredItemErrors = Object.fromEntries(
      Object.entries(itemError).filter(([_, value]) => value !== '')
    );

    // Verificar que al menos un campo (además de id) esté presente
    const updateFields = Object.keys(item).filter((key) => key !== 'id');
    if (updateFields.length === ZERO) {
      itemError._general = 'At least one field must be provided for update';
    } else {
      hasValidUpdate = true;
    }

    if (Object.keys(filteredItemErrors).length > ZERO) {
      itemErrors[index] = filteredItemErrors;
    }
  });

  if (itemErrors.length > ZERO) {
    errors.items = itemErrors;
  }

  if (!hasValidUpdate) {
    errors._general = 'At least one item must have fields to update';
  }

  const isValid = Object.keys(errors).length === ZERO;
  return { errors, isValid };
};

// Validación individual de campo
export const validateOrderDetailField = (fieldName, value) => {
  const validators = {
    quantity: validateQuantity,
    historical_price: validateHistoricalPrice,
    order: validateOrder,
    product: validateProduct,
  };

  if (!validators[fieldName]) {
    return '';
  }

  return validators[fieldName](value);
};

// Utilidad para calcular subtotal
export const calculateSubtotal = (quantity, historicalPrice) => {
  const qty = parseInt(quantity) || ZERO;
  const price = parseFloat(historicalPrice) || ZERO;
  return (qty * price).toFixed(2);
};

// Validación para order details by order
export const validateOrderIdParam = (orderId) => {
  if (!orderId) return 'Valid order ID is required';
  if (typeof orderId !== 'string' || !MONGO_ID_REGEX.test(orderId))
    return 'Valid order ID is required';
  return '';
};
