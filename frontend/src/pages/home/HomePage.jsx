import { HomeTemplate } from '../../components/templates/home_layout/HomeTemplate';
import { ProductGrid } from '../../components/organisms/product_grid/ProductGrid';
import { DiscountProductGrid } from '../../components/organisms/product_grid/DiscountProductGrid';
import { useHomePageLogic } from './homePageLogic';
import homeImage from '../../assets/images/home.jpg';
import { useMemo } from 'react';

export default function HomePage() {
  const { discountProducts, regularProducts, loading, handleAddToCart } =
    useHomePageLogic();

  const DiscountProductContent = useMemo(
    () => (
      <DiscountProductGrid
        products={discountProducts}
        onAddToCart={handleAddToCart} // AÑADIDO
      />
    ),
    [discountProducts, handleAddToCart]
  );

  const productContent = useMemo(
    () => (
      <ProductGrid
        products={regularProducts}
        onAddToCart={handleAddToCart} // AÑADIDO
      />
    ),
    [regularProducts, handleAddToCart]
  );

  return (
    <div>
      <HomeTemplate
        homeImage={homeImage}
        discountProductContent={DiscountProductContent}
        productContent={productContent}
        isLoading={loading}
      />
    </div>
  );
}
