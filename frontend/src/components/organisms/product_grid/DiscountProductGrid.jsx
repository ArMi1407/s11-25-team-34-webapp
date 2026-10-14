import { DiscountProductCard } from '../../molecules/cards/DiscountProductCard';
import { memo } from 'react';

export const DiscountProductGrid = memo(({ products, onAddToCart }) => {
  if (!products) return null;
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-4 sm:gap-4 lg:gap-8">
      {products.map((product) => {
        const discountedPrice = (product.price * 0.81).toFixed(2);

        return (
          <DiscountProductCard
            key={product.id}
            imageSrc={product.imageUrl}
            name={product.name}
            price={product.price}
            discountedPrice={discountedPrice}
            ecoBadge={product.ecoBadge}
            productId={product.id}
            onAddToCart={onAddToCart}
          />
        );
      })}
    </div>
  );
});
