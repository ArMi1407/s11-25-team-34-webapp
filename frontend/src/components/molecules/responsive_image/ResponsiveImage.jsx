// ==========================================
//
// Description: Responsive Image
//
// File: ResponsiveImage.jsx
// Author: Anthony Bañon
// Created: 2025-11-25
// Last Updated: 2025-11-25
// ==========================================

import { Image } from '../../atoms/image/Image';

export const ResponsiveImage = ({
  mobileSrc,
  desktopSrc,
  alt = '',
  className = '',
}) => {
  return (
    <>
      {/* mobile*/}
      <Image src={mobileSrc} alt={alt} className={`${className} sm:hidden`} />
      {/* desktop */}
      <Image
        src={desktopSrc}
        alt={alt}
        className={`${className} hidden sm:block`}
      />
    </>
  );
};
