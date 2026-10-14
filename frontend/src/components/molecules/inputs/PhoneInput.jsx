// ==========================================
//
// Description: Phone Input Component
//
// File: PhoneInput.jsx
// Author: Anthony Bañon
// Created: 2025-11-29
// Last Updated: 2025-11-29
// ==========================================

import { Input } from '../../atoms/input/Input';

export const PhoneInput = ({ hasError, label = 'Phone', ...props }) => {
  const variant = hasError ? 'error' : 'default';

  return (
    <div className="w-full">
      <Input variant={variant} type="tel" placeholder={label} {...props} />
    </div>
  );
};
