// CartContext.jsx
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
} from 'react';
import { cartService } from '../services/cart/cartService';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cartCount, setCartCount] = useState(0);
  const [cartData, setCartData] = useState(null);
  const [cartLoading, setCartLoading] = useState(true);
  const [cartError, setCartError] = useState(null);
  const [isMerging, setIsMerging] = useState(false);

  // Fetch cart data
  const refreshCart = useCallback(async () => {
    try {
      setCartLoading(true);
      setCartError(null);

      const cartResponse = await cartService.getCart();
      const formattedCart = cartService.formatCartForUI(
        cartResponse.data || cartResponse
      );
      setCartData(formattedCart);
      setCartCount(cartService.getItemCount(formattedCart));

      // Sync with localStorage for offline support
      cartService.syncCartWithLocalStorage(formattedCart);
    } catch (error) {
      console.error('Error refreshing cart:', error);
      setCartError(error.message || 'Failed to load cart');

      // Try to load from localStorage as fallback
      const localCart = cartService.getCartFromLocalStorage();
      if (localCart) {
        setCartData(localCart);
        setCartCount(cartService.getItemCount(localCart));
      }
    } finally {
      setCartLoading(false);
    }
  }, []);

  // Initial cart load
  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  // Add item to cart
  const addToCart = async (productId, quantity = 1) => {
    try {
      setCartError(null);
      const response = await cartService.addItem(productId, quantity);

      // Optimistic update - update UI immediately
      const optimisticCount = cartCount + quantity;
      setCartCount(optimisticCount);

      // Then refresh cart to get exact data
      await refreshCart();

      return response;
    } catch (error) {
      console.error('Error adding to cart:', error);
      setCartError(error.message || 'Failed to add item to cart');
      throw error;
    }
  };

  // Update cart item quantity
  const updateCartItem = async (itemId, quantity) => {
    try {
      setCartError(null);
      const response = await cartService.updateItem(itemId, quantity);
      await refreshCart();
      return response;
    } catch (error) {
      console.error('Error updating cart item:', error);
      setCartError(error.message || 'Failed to update cart item');
      throw error;
    }
  };

  // Remove item from cart
  const removeCartItem = async (itemId) => {
    try {
      setCartError(null);
      const response = await cartService.removeItem(itemId);
      await refreshCart();
      return response;
    } catch (error) {
      console.error('Error removing cart item:', error);
      setCartError(error.message || 'Failed to remove item from cart');
      throw error;
    }
  };

  // Clear entire cart
  const clearCart = async () => {
    try {
      setCartError(null);
      const response = await cartService.clearCart();

      // Optimistic update
      setCartCount(0);
      setCartData(null);

      // Clear localStorage
      cartService.clearCartFromLocalStorage();

      return response;
    } catch (error) {
      console.error('Error clearing cart:', error);
      setCartError(error.message || 'Failed to clear cart');
      throw error;
    }
  };

  // Checkout
  const checkout = async (shippingAddress) => {
    try {
      setCartError(null);

      // Validate cart before checkout
      const validation = cartService.validateCartBeforeCheckout(cartData);
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '));
      }

      const response = await cartService.checkout(shippingAddress);

      // Clear cart after successful checkout
      setCartCount(0);
      setCartData(null);
      cartService.clearCartFromLocalStorage();

      return cartService.formatCheckoutForUI(response.data || response);
    } catch (error) {
      console.error('Error during checkout:', error);
      setCartError(error.message || 'Checkout failed');
      throw error;
    }
  };

  // Merge carts after login
  const mergeCarts = async () => {
    try {
      setIsMerging(true);
      setCartError(null);

      const response = await cartService.mergeCarts();

      // Refresh cart after merge
      await refreshCart();

      return response;
    } catch (error) {
      console.error('Error merging carts:', error);
      setCartError(error.message || 'Failed to merge carts');
      throw error;
    } finally {
      setIsMerging(false);
    }
  };

  // Add to cart with optimistic update (smart add)
  const addToCartOptimistic = async (product, quantity = 1) => {
    try {
      setCartError(null);

      // Check if product already exists in cart
      const existingItem = cartData?.items?.find(
        (item) => item.product?.id === product.id
      );

      let response;

      if (existingItem) {
        // Update quantity if exists
        console.log('🧩 existingItem encontrado:', existingItem);

        const newQuantity = existingItem.quantity + quantity;
        response = await updateCartItem(existingItem.id, newQuantity);
      } else {
        // Add new item
        response = await addToCart(product.id, quantity);
      }

      return response;
    } catch (error) {
      console.error('Error in optimistic add to cart:', error);
      setCartError(error.message || 'Failed to add item to cart');
      throw error;
    }
  };

  // Get cart summary
  const getCartSummary = useCallback(async () => {
    try {
      const summary = await cartService.getCartSummary();
      return summary;
    } catch (error) {
      console.error('Error getting cart summary:', error);
      return null;
    }
  }, []);

  // Check if cart is empty
  const isCartEmpty = useMemo(() => {
    return cartService.isCartEmpty(cartData);
  }, [cartData]);

  // Get cart total price
  const getCartTotal = useMemo(() => {
    return cartService.getCartTotal(cartData);
  }, [cartData]);

  // Calculate cart item count (detailed)
  const getDetailedItemCount = useMemo(() => {
    if (!cartData?.items) return 0;
    return cartData.items.reduce((total, item) => total + item.quantity, 0);
  }, [cartData]);

  // Get item by product ID
  const getCartItemByProductId = useCallback(
    (productId) => {
      if (!cartData?.items) return null;
      return cartData.items.find((item) => item.product?.id === productId);
    },
    [cartData]
  );

  // Calculate carbon footprint by item
  const getCarbonFootprintByItem = useCallback(
    (itemId) => {
      if (!cartData?.items) return 0;
      const item = cartData.items.find((item) => item.id === itemId);
      return item ? item.totalCarbon : 0;
    },
    [cartData]
  );

  // Context value
  const contextValue = useMemo(
    () => ({
      // State
      cartCount,
      cartData,
      cartLoading,
      cartError,
      isMerging,

      // Computed values
      isCartEmpty,
      cartTotal: getCartTotal,
      detailedItemCount: getDetailedItemCount,

      // Actions
      refreshCart,
      addToCart,
      updateCartItem,
      removeCartItem,
      clearCart,
      checkout,
      mergeCarts,
      addToCartOptimistic,

      // Helper functions
      getCartSummary,
      getCartItemByProductId,
      getCarbonFootprintByItem,

      // Validation
      validateCart: () => cartService.validateCartBeforeCheckout(cartData),
    }),
    [
      cartCount,
      cartData,
      cartLoading,
      cartError,
      isMerging,
      isCartEmpty,
      getCartTotal,
      getDetailedItemCount,
      refreshCart,
      getCartSummary,
      getCartItemByProductId,
      getCarbonFootprintByItem,
    ]
  );

  return (
    <CartContext.Provider value={contextValue}>{children}</CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within CartProvider');
  }
  return context;
};

// Hook for cart item operations
export const useCartItem = (productId) => {
  const { cartData, updateCartItem, removeCartItem, getCartItemByProductId } =
    useCart();

  const item = getCartItemByProductId(productId);

  const updateQuantity = async (newQuantity) => {
    if (!item) return null;
    return updateCartItem(item.id, newQuantity);
  };

  const removeFromCart = async () => {
    if (!item) return null;
    return removeCartItem(item.id);
  };

  return {
    item,
    isInCart: !!item,
    quantity: item?.quantity || 0,
    updateQuantity,
    removeFromCart,
  };
};

// Hook for cart summary
export const useCartSummary = () => {
  const {
    cartData,
    cartTotal,
    isCartEmpty,
    detailedItemCount,
    getCartSummary,
  } = useCart();

  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSummary = async () => {
      if (!cartData) return;

      setLoading(true);
      try {
        const data = await getCartSummary();
        setSummary(data);
      } catch (error) {
        console.error('Error fetching cart summary:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [cartData, getCartSummary]);

  return {
    summary,
    loading,
    cartTotal,
    isCartEmpty,
    itemCount: detailedItemCount,
    items: cartData?.items || [],
  };
};
