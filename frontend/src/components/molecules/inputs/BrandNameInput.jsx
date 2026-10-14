// ==========================================
//
// Description: Brand Name Input Component
//
// File: BrandNameInput.jsx
// Author: Anthony Bañon
// Created: 2025-11-29
// Last Updated: 2025-11-29
// ==========================================

import { Input } from '../../atoms/input/Input';

export const BrandNameInput = ({ hasError, ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input
        variant={variant}
        type="text"
        placeholder="Brand Name"
        {...props}
      />
    </div>
  );
};
