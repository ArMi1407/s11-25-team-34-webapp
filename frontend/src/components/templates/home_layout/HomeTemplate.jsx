// ==========================================
//
// Description: Home Template
//
// File: HomeTemplate.jsx
// Author: Anthony Bañon
// Created: 2025-11-25
// Last Updated: 2025-11-25
// ==========================================

import { HomeHeader } from '../../organisms/home_header/HomeHeader';
import { HomeImageWithText } from '../../molecules/ImageWithText/HomeImageWithText';
import { LoadingSpinner } from '../../atoms/spinner/LoadingSpinner';
import { Title } from '../../atoms/text/Title';

export const HomeTemplate = ({
  children,
  homeImage,
  productContent,
  discountProductContent,
  isLoading = false,
}) => {
  return (
    <div className="bg-bg-body">
      <HomeHeader />
      <HomeImageWithText
        imageSrc={homeImage}
        alt="Productos ecológicos"
        title="Compra productos sostenibles"
        description="Encuentra productos amigables con el medio ambiente"
        subDescription="Eco-friendly, eco beautiful"
        textPosition="top-left"
        // overlayOpacity={30}
      />
      <Title
        className="text-text-primary mt-8 text-lg sm:text-2xl md:text-3xl lg:text-5xl px-4 sm:px-8 lg:px-8 "
        variant="title"
      >
        Productos con Descuento.
      </Title>
      <div className="max-w-screen-2xl mx-auto px-6 sm:px-8 lg:px-8 mt-8">
        {isLoading ? (
          <LoadingSpinner message="Loading products..." />
        ) : (
          discountProductContent
        )}
      </div>
      <Title
        className="text-text-primary mt-8 text-lg sm:text-2xl md:text-3xl lg:text-5xl px-4 sm:px-8 lg:px-8 "
        variant="title"
      >
        Productos Destacados.
      </Title>
      {/* ✅ Container layout en template */}
      <div className="max-w-screen-2xl mx-auto px-6 sm:px-8 lg:px-8 mt-8">
        {isLoading ? (
          <LoadingSpinner message="Loading products..." />
        ) : (
          productContent
        )}
      </div>
      <div className="h-8 lg:h-16"></div>

      {children}
    </div>
  );
};
