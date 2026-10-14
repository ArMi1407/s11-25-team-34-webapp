// CardCartList.jsx - CORREGIDO
import { CardCart } from '../../molecules/cards/CardCart';
import { memo } from 'react';

export const CardCartList = memo(
  ({ products, onQuantityChange, onRemoveItem }) => {
    if (!products || products.length === 0) {
      return (
        <div className="text-center py-12">
          <p className="text-text-secondary text-lg">Tu carrito está vacío</p>
        </div>
      );
    }

    return (
      <div className="flex flex-col gap-4 md:gap-6">
        {products.map((product) => (
          <CardCart
            key={product.id}
            imageSrc={product.imageUrl}
            name={product.name}
            price={product.price}
            ecoBadge={product.ecoBadge}
            quantity={product.quantity}
            onQuantityChange={
              (newQuantity) => onQuantityChange(product.id, newQuantity) // Ahora pasa cartItemId
            }
            onRemove={() => onRemoveItem(product.id)} // Ahora pasa cartItemId
          />
        ))}
      </div>
    );
  }
);
