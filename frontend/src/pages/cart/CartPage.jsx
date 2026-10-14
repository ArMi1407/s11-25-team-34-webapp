// CartPage.jsx
import { CartTemplate } from '../../components/templates/cart_layout/CartTemplate';
import { CardCartList } from '../../components/organisms/cart/CardCartList';
import { useCartPageLogic } from './cartPageLogic';
import { LoadingSpinner } from '../../components/atoms/spinner/LoadingSpinner';
import { ErrorMessage } from '../../components/atoms/error/ErrorMessage'; // Añade este componente si no existe
import { useMemo } from 'react';

export default function CartPage() {
  const {
    cartItems,
    subtotal,
    tax,
    shipping,
    loading,
    error,
    handleQuantityChange,
    handleRemoveItem,
    handleCheckout,
  } = useCartPageLogic();

  const cartContent = useMemo(() => {
    if (loading) {
      return <LoadingSpinner message="Cargando carrito..." />;
    }

    if (error) {
      return (
        <ErrorMessage
          message={error}
          onRetry={() => window.location.reload()}
        />
      );
    }

    if (!cartItems || cartItems.length === 0) {
      return (
        <div className="text-center py-12">
          <p className="text-text-secondary text-lg">Tu carrito está vacío</p>
        </div>
      );
    }

    return (
      <CardCartList
        products={cartItems}
        onQuantityChange={handleQuantityChange}
        onRemoveItem={handleRemoveItem}
      />
    );
  }, [cartItems, loading, error, handleQuantityChange, handleRemoveItem]);

  return (
    <CartTemplate
      cartItems={cartItems}
      subtotal={subtotal}
      tax={tax}
      shipping={shipping}
      onCheckout={handleCheckout}
      isLoading={loading}
      hasError={!!error}
    >
      {cartContent}
    </CartTemplate>
  );
}
