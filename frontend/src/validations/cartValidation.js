// ==========================================
//
// Description: Cart Validation
//
// File: cartValidation.js
// Author: Anthony Bañon
// Created: 2025-12-11
// Last Updated: 2025-12-11
// ==========================================

// Constants matching Django backend
const MAX_CART_QUANTITY = 99; // Max quantity per product
const MAX_SHIPPING_ADDRESS_LENGTH = 500;

// Regular expressions
const QUANTITY_REGEX = /^[1-9][0-9]?$|^99$/; // 1-99
const POSTAL_CODE_REGEX = /^[A-Z0-9\s-]{3,10}$/;
const PHONE_REGEX = /^[\d\s+\-()]{10,20}$/;

// Individual validation functions
export const validateProductId = (productId) => {
  if (!productId && productId !== 0) return 'Product ID is required';
  const numId = parseInt(productId);
  if (isNaN(numId)) return 'Product ID must be a valid number';
  if (numId < 1) return 'Product ID must be greater than 0';
  return '';
};

export const validateQuantity = (quantity) => {
  if (!quantity && quantity !== 0) return 'Quantity is required';
  const numQuantity = parseInt(quantity);
  if (isNaN(numQuantity)) return 'Quantity must be a valid integer';
  if (numQuantity < 1) return 'Quantity must be at least 1';
  if (numQuantity > MAX_CART_QUANTITY)
    return `Cannot add more than ${MAX_CART_QUANTITY} of the same product`;
  if (!QUANTITY_REGEX.test(quantity.toString()))
    return 'Quantity must be between 1 and 99';
  return '';
};

export const validateQuantityDelta = (quantityDelta) => {
  if (!quantityDelta && quantityDelta !== 0)
    return 'Quantity delta is required';
  const numDelta = parseInt(quantityDelta);
  if (isNaN(numDelta)) return 'Quantity delta must be a valid integer';
  if (numDelta === 0) return 'Quantity delta cannot be 0';
  if (Math.abs(numDelta) > MAX_CART_QUANTITY)
    return `Quantity change cannot exceed ${MAX_CART_QUANTITY}`;
  return '';
};

export const validateCartItemId = (itemId) => {
  if (!itemId && itemId !== 0) return 'Cart item ID is required';
  const numId = parseInt(itemId);
  if (isNaN(numId)) return 'Cart item ID must be a valid number';
  if (numId < 1) return 'Cart item ID must be greater than 0';
  return '';
};

// Shipping address validation
export const validateShippingAddress = (address) => {
  if (!address) return 'Shipping address is required';
  if (typeof address !== 'object') return 'Shipping address must be an object';

  const errors = {};

  // Required fields
  const requiredFields = ['street', 'city', 'state', 'postal_code', 'country'];
  requiredFields.forEach((field) => {
    if (!address[field] || address[field].trim() === '') {
      errors[field] = `${field.replace('_', ' ').toUpperCase()} is required`;
    }
  });

  // Validate postal code
  if (address.postal_code && !POSTAL_CODE_REGEX.test(address.postal_code)) {
    errors.postal_code = 'Invalid postal code format';
  }

  // Validate phone if provided
  if (address.phone && !PHONE_REGEX.test(address.phone)) {
    errors.phone = 'Invalid phone number format';
  }

  // Validate email if provided
  if (address.email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(address.email)) {
      errors.email = 'Invalid email format';
    }
  }

  // Validate total length
  const addressStr = JSON.stringify(address);
  if (addressStr.length > MAX_SHIPPING_ADDRESS_LENGTH) {
    errors._general = `Shipping address too long (max ${MAX_SHIPPING_ADDRESS_LENGTH} characters)`;
  }

  const isValid = Object.keys(errors).length === 0;
  return { errors, isValid };
};

// Complete form validation
export const validateAddToCartForm = (formData) => {
  const errors = {};

  errors.product_id = validateProductId(formData.product_id);
  errors.quantity = validateQuantity(formData.quantity);

  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== '')
  );

  const isValid = Object.keys(filteredErrors).length === 0;
  return { errors: filteredErrors, isValid };
};

export const validateUpdateCartItemForm = (formData) => {
  const errors = {};

  errors.quantity = validateQuantityDelta(formData.quantity);

  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== '')
  );

  const isValid = Object.keys(filteredErrors).length === 0;
  return { errors: filteredErrors, isValid };
};

export const validateCheckoutForm = (formData) => {
  const { errors, isValid } = validateShippingAddress(
    formData.shipping_address
  );

  if (errors._general) {
    return { errors: { shipping_address: errors._general }, isValid: false };
  }

  if (!isValid) {
    return { errors: { shipping_address: errors }, isValid: false };
  }

  return { errors: {}, isValid: true };
};

// Field validation helper
export const validateCartField = (fieldName, value) => {
  const validators = {
    product_id: validateProductId,
    quantity: validateQuantity,
    quantity_delta: validateQuantityDelta,
    cart_item_id: validateCartItemId,
  };

  if (!validators[fieldName]) {
    return '';
  }

  return validators[fieldName](value);
};

// Cart item transformation helpers
export const formatCartItemForApi = (cartItem) => {
  return {
    product_id: cartItem.product?.id || cartItem.product_id,
    quantity: cartItem.quantity || 1,
  };
};

export const formatCheckoutDataForApi = (shippingAddress) => {
  return {
    shipping_address: {
      street: shippingAddress.street?.trim() || '',
      city: shippingAddress.city?.trim() || '',
      state: shippingAddress.state?.trim() || '',
      postal_code: shippingAddress.postal_code?.trim() || '',
      country: shippingAddress.country?.trim() || '',
      ...(shippingAddress.phone && { phone: shippingAddress.phone.trim() }),
      ...(shippingAddress.email && { email: shippingAddress.email.trim() }),
      ...(shippingAddress.additional_info && {
        additional_info: shippingAddress.additional_info.trim(),
      }),
    },
  };
};

// Cart summary calculations
export const calculateCartSummary = (cartItems) => {
  const subtotal = cartItems.reduce(
    (sum, item) =>
      sum + (item.product?.price || item.price) * (item.quantity || 1),
    0
  );

  const totalItems = cartItems.reduce(
    (sum, item) => sum + (item.quantity || 1),
    0
  );

  const totalCarbonFootprint = cartItems.reduce(
    (sum, item) =>
      sum +
      (item.product?.carbon_footprint || item.carbon_footprint || 0) *
        (item.quantity || 1),
    0
  );

  return {
    subtotal,
    totalItems,
    totalCarbonFootprint,
    tax: subtotal * 0.16, // 16% tax
    shipping: subtotal > 50 ? 0 : 5.99,
  };
};

// Helper to check if cart is empty
export const isCartEmpty = (cartItems) => {
  return !cartItems || cartItems.length === 0;
};

// Helper to find item in cart
export const findCartItem = (cartItems, productId) => {
  return cartItems.find(
    (item) => item.product?.id === productId || item.product_id === productId
  );
};

// Helper to calculate item total
export const calculateItemTotal = (item) => {
  return (item.product?.price || item.price) * (item.quantity || 1);
};
