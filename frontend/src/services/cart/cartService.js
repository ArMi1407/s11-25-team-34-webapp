// ==========================================
//
// Description: Cart Service for Django API
//
// File: cartService.js
// Author: Anthony Bañon
// Created: 2025-12-11
// Last Updated: 2025-12-11
// ==========================================

import { api } from '../api';
import * as cartValidation from '../../validations/cartValidation';

const BASE =
  import.meta.env.VITE_API_URL?.replace('/api', '') || 'http://localhost:8000';

export const cartService = {
  // Get current cart
  async getCart() {
    try {
      const response = await api.get('/cart/');
      return response;
    } catch (error) {
      console.error('Error fetching cart:', error);
      throw error;
    }
  },

  // Add item to cart
  async addItem(productId, quantity) {
    // Validate input
    const validation = cartValidation.validateAddToCartForm({
      product_id: productId,
      quantity: quantity,
    });

    if (!validation.isValid) {
      throw new Error(Object.values(validation.errors).join(', '));
    }

    try {
      const response = await api.post('/cart/add_item/', {
        product_id: productId,
        quantity: quantity,
      });

      return response;
    } catch (error) {
      console.error('Error adding item to cart:', error);
      throw error;
    }
  },

  // Update cart item quantity
  async updateItem(itemId, quantity) {
    // Validate input
    const validation = cartValidation.validateUpdateCartItemForm({
      quantity: quantity,
    });

    if (!validation.isValid) {
      throw new Error(Object.values(validation.errors).join(', '));
    }

    try {
      const response = await api.put(`/cart/items/${itemId}/`, {
        quantity: quantity,
      });

      return response;
    } catch (error) {
      console.error('Error updating cart item:', error);
      throw error;
    }
  },

  // Remove item from cart
  async removeItem(itemId) {
    // Validate input
    const itemIdError = cartValidation.validateCartItemId(itemId);
    if (itemIdError) {
      throw new Error(itemIdError);
    }

    try {
      const response = await api.delete(`/cart/items/${itemId}/`);
      return response;
    } catch (error) {
      console.error('Error removing item from cart:', error);
      throw error;
    }
  },

  // Clear entire cart
  async clearCart() {
    try {
      const response = await api.delete('/cart/clear/');
      return response;
    } catch (error) {
      console.error('Error clearing cart:', error);
      throw error;
    }
  },

  // Checkout
  async checkout(shippingAddress) {
    // Validate input
    const validation = cartValidation.validateCheckoutForm({
      shipping_address: shippingAddress,
    });

    if (!validation.isValid) {
      throw new Error(Object.values(validation.errors).join(', '));
    }

    try {
      const formattedData =
        cartValidation.formatCheckoutDataForApi(shippingAddress);
      const response = await api.post('/cart/checkout/', formattedData);

      return response;
    } catch (error) {
      console.error('Error during checkout:', error);
      throw error;
    }
  },

  // Merge guest cart with user cart (after login)
  async mergeCarts() {
    try {
      const response = await api.post('/cart/merge/');
      return response;
    } catch (error) {
      console.error('Error merging carts:', error);
      throw error;
    }
  },

  // Helper: Add to cart with existing cart data (optimistic update)
  async addToCartWithOptimisticUpdate(product, quantity = 1, currentCart) {
    // Validate input
    const validation = cartValidation.validateAddToCartForm({
      product_id: product.id,
      quantity: quantity,
    });

    if (!validation.isValid) {
      throw new Error(Object.values(validation.errors).join(', '));
    }

    // Check if product already exists in cart
    const existingItem = currentCart?.items?.find(
      (item) => item.product?.id === product.id
    );

    if (existingItem) {
      // Update quantity if exists
      const newQuantity = existingItem.quantity + quantity;
      return this.updateItem(existingItem.id, newQuantity);
    } else {
      // Add new item
      return this.addItem(product.id, quantity);
    }
  },

  // Helper: Get cart summary
  async getCartSummary() {
    try {
      const cart = await this.getCart();

      // Calculate additional summary if needed
      const summary = cartValidation.calculateCartSummary(cart.items || []);

      return {
        ...cart,
        summary: {
          ...summary,
          totalPrice: cart.total_price || summary.subtotal,
          totalItems: cart.total_items || summary.totalItems,
          totalCarbonFootprint:
            cart.total_carbon_footprint || summary.totalCarbonFootprint,
        },
      };
    } catch (error) {
      console.error('Error getting cart summary:', error);
      throw error;
    }
  },

  // Helper: Format cart data for UI
  formatCartForUI(cartData) {
    if (!cartData) return null;

    return {
      id: cartData.id,
      userId: cartData.user,
      totalItems: cartData.total_items || 0,
      totalPrice: parseFloat(cartData.total_price || 0),
      totalCarbonFootprint: parseFloat(cartData.total_carbon_footprint || 0),
      createdAt: cartData.created_at,
      updatedAt: cartData.updated_at,

      items: (cartData.items || []).map((item) => {
        const p = item.product || {};

        // SIEMPRE UNIFICAMOS AQUÍ
        let imageUrl = null;
        if (p.image_url) {
          imageUrl = p.image_url.startsWith('http')
            ? p.image_url
            : `${BASE}${p.image_url}`;
        }

        return {
          id: item.id,
          productId: p.id,
          name: p.name,
          price: parseFloat(p.price || 0),
          ecoBadge: p.eco_badge || '🌿 medium Impact',
          quantity: item.quantity,
          addedAt: item.added_at,
          totalPrice: parseFloat(item.total_price || 0),
          totalCarbon: parseFloat(item.total_carbon || 0),

          // 🔥 CAMPO ÚNICO QUE ULTILIZA CART UI
          imageUrl,

          // nested product (opcional)
          product: {
            id: p.id,
            name: p.name,
            price: parseFloat(p.price || 0),
            imageUrl, // también unificado
            carbonFootprint: parseFloat(p.carbon_footprint || 0),
            ecoBadge: p.eco_badge,
          },
        };
      }),
    };
  },

  // Helper: Format checkout data for UI
  formatCheckoutForUI(checkoutData) {
    if (!checkoutData) return null;

    return {
      orderNumber: checkoutData.data?.order_number,
      totalAmount: parseFloat(checkoutData.data?.total_amount || 0),
      totalCarbonFootprint: parseFloat(
        checkoutData.data?.total_carbon_footprint || 0
      ),
      status: checkoutData.data?.status,
      orderId: checkoutData.data?.order_id,
      message: checkoutData.message,
    };
  },

  // Helper: Check if cart is empty
  isCartEmpty(cartData) {
    return cartValidation.isCartEmpty(cartData?.items);
  },

  // Helper: Get item count
  getItemCount(cartData) {
    return (
      cartData?.total_items ||
      (cartData?.items || []).reduce(
        (sum, item) => sum + (item.quantity || 1),
        0
      ) ||
      0
    );
  },

  // Helper: Get cart total
  getCartTotal(cartData) {
    return parseFloat(cartData?.total_price || 0);
  },

  // Helper: Sync cart with local storage for offline support
  syncCartWithLocalStorage(cartData) {
    try {
      if (cartData) {
        localStorage.setItem('cart_data', JSON.stringify(cartData));
        localStorage.setItem('cart_last_sync', new Date().toISOString());
      }
    } catch (error) {
      console.warn('Could not save cart to localStorage:', error);
    }
  },

  // Helper: Get cart from local storage
  getCartFromLocalStorage() {
    try {
      const cartData = localStorage.getItem('cart_data');
      return cartData ? JSON.parse(cartData) : null;
    } catch (error) {
      console.warn('Could not load cart from localStorage:', error);
      return null;
    }
  },

  // Helper: Clear cart from local storage
  clearCartFromLocalStorage() {
    try {
      localStorage.removeItem('cart_data');
      localStorage.removeItem('cart_last_sync');
    } catch (error) {
      console.warn('Could not clear cart from localStorage:', error);
    }
  },

  // Helper: Validate cart before checkout
  validateCartBeforeCheckout(cartData) {
    const errors = [];

    if (cartValidation.isCartEmpty(cartData.items)) {
      errors.push('Cart is empty');
      return { isValid: false, errors };
    }

    // Check each item
    cartData.items.forEach((item, index) => {
      if (!item.product) {
        errors.push(`Item ${index + 1}: Product information missing`);
      }

      if (!item.quantity || item.quantity < 1) {
        errors.push(
          `Item "${item.product?.name || 'Unknown'}": Invalid quantity`
        );
      }
    });

    return {
      isValid: errors.length === 0,
      errors: errors.length > 0 ? errors : null,
    };
  },
};
