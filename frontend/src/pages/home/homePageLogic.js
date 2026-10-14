// homePageLogic.js
// ==========================================
//
// Description: Home Page Business Logic
//
// File: homePageLogic.js
// Author: Anthony Bañon
// Created: [Fecha]
// Last Updated: [Fecha]
// ==========================================

import { productService } from '../../services/products/productService';
import { useNotification } from '../../hooks/useNotification';
import { useState, useEffect } from 'react';
import { useCart } from '../../contexts/CartContext'; // IMPORTANTE: Añadir esto

export const useHomePageLogic = () => {
  const { showSuccess, showError } = useNotification();
  const {
    addToCartOptimistic, // Usar esta función en lugar de cartService.addItem
    cartCount, // Usar esto en lugar de cartItemCount
    refreshCart, // Usar esto si necesitas refrescar
  } = useCart(); // Obtener funciones del contexto

  const [regularProducts, setRegularProducts] = useState([]);
  const [discountProducts, setDiscountProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  // REMOVER: const [cartItemCount, setCartItemCount] = useState(0); // Ya no necesitamos esto

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);

        // 1. Cargar productos (esto sigue igual)
        const response = await productService.getAll();
        const productsData = response.results || [];

        const transformedProducts = productsData.map((product) => ({
          id: product.id,
          name: product.name,
          imageUrl: product.image_url,
          price: product.price,
          ecoBadge: product.eco_badge,
        }));

        // 🔥 Shuffle function
        const shuffle = (arr) =>
          arr
            .map((value) => ({ value, sort: Math.random() }))
            .sort((a, b) => a.sort - b.sort)
            .map(({ value }) => value);

        // Primer grupo random (descuentos)
        const discountList = shuffle(transformedProducts).slice(0, 8);

        // Segundo grupo random distinto:
        const remaining = transformedProducts.filter(
          (p) => !discountList.some((d) => d.id === p.id)
        );

        const regularList = shuffle(remaining).slice(0, 8);

        setDiscountProducts(discountList);
        setRegularProducts(regularList);

        // 2. El contador del carrito ahora viene del contexto
        // Ya no necesitamos cargarlo manualmente aquí
        // El CartProvider ya lo carga automáticamente
      } catch (error) {
        console.error('Error in home page logic:', error);
        showError('Failed to load products');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []); // ✅ Empty dependency array - se ejecuta solo al montar

  // Función para añadir al carrito - AHORA CON CONTEXTO
  const handleAddToCart = async (productId) => {
    console.log('ID RECIBIDO EN ADD:', productId, typeof productId);
    const id = Number(productId);
    try {
      // Buscar el producto en los arrays ya cargados
      const allProducts = [...discountProducts, ...regularProducts];
      const product = allProducts.find((p) => p.id === id);

      if (!product) {
        throw new Error('Product not found');
      }

      // Usar la función del contexto en lugar de cartService
      await addToCartOptimistic(product, 1);
      await refreshCart(); // 👈 AGREGAR ESTO

      // NOTA: El contador se actualiza automáticamente en el contexto
      // No necesitamos setCartItemCount((prev) => prev + 1);

      showSuccess('Producto añadido al carrito');
    } catch (error) {
      console.error('Error adding to cart:', error);
      showError(error.message || 'Error al añadir al carrito');
    }
  };

  // Función para refrescar contador del carrito - AHORA CON CONTEXTO
  const refreshCartCount = async () => {
    // Simplemente llamamos a refreshCart del contexto
    await refreshCart();
  };

  return {
    discountProducts,
    regularProducts,
    loading,
    cartItemCount: cartCount, // Usamos cartCount del contexto
    handleAddToCart,
    refreshCartCount,
  };
};
