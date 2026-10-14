// cartPageLogic.js
import { useCart } from '../../contexts/CartContext';
import { useNotification } from '../../hooks/useNotification';
import { useState } from 'react';

export const useCartPageLogic = () => {
  const {
    cartData,
    cartLoading: contextLoading,
    cartError,
    updateCartItem,
    removeCartItem,
    checkout,
    refreshCart,
    validateCart,
  } = useCart();

  const { showSuccess, showError } = useNotification();
  const [localLoading, setLocalLoading] = useState(false);

  const cartItems = cartData?.items || [];

  // Cambiar cantidad de un item
  const handleQuantityChange = async (productId, newQuantity) => {
    try {
      setLocalLoading(true);
      const item = cartItems.find((item) => item.id === productId);
      if (!item) {
        throw new Error('Item no encontrado en el carrito');
      }

      await updateCartItem(item.id, newQuantity);
      showSuccess('Cantidad actualizada');
    } catch (error) {
      console.error('Error updating quantity:', error);
      showError(error.message || 'Error al actualizar cantidad');
    } finally {
      setLocalLoading(false);
    }
  };
  console.log('CART DATA ACTUAL:', cartData);
  // Eliminar item del carrito
  const handleRemoveItem = async (itemId) => {
    try {
      setLocalLoading(true);
      await removeCartItem(itemId);
      showSuccess('Producto eliminado del carrito');
    } catch (error) {
      console.error('Error removing item:', error);
      showError('Error al eliminar producto');
    } finally {
      setLocalLoading(false);
    }
  };

  // Procesar checkout
  const handleCheckout = async (shippingAddress) => {
    try {
      setLocalLoading(true);

      // Validar carrito antes del checkout
      const validation = validateCart();
      if (!validation.isValid) {
        showError(validation.errors.join(', '));
        return null;
      }

      const result = await checkout(shippingAddress);
      showSuccess('¡Compra realizada con éxito!');

      return result;
    } catch (error) {
      console.error('Error during checkout:', error);
      showError(error.message || 'Error al procesar el pago');
      throw error;
    } finally {
      setLocalLoading(false);
    }
  };

  // Calcular totales (ahora basados en cartData del contexto)
  const subtotal = cartData?.totalPrice || 0;
  const tax = subtotal * 0.16; // IVA 16%
  const shipping = subtotal > 50 ? 0 : 5.99; // Envío gratis sobre $50
  const total = subtotal + tax + shipping;

  return {
    cartItems,
    cartData,
    subtotal,
    tax,
    shipping,
    total,
    loading: contextLoading || localLoading,
    error: cartError,
    handleQuantityChange,
    handleRemoveItem,
    handleCheckout,
    refreshCart,
  };
};
