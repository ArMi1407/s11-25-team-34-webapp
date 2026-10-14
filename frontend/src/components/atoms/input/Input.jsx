// ==========================================
//
// Description: Input
//
// File: Input.jsx
// Author: Anthony Bañon
// Created: 2025-11-11
// Last Updated: 2025-11-11
// ==========================================

export const Input = ({ variant = 'default', className = '', ...props }) => {
  const baseStyles =
    'font-inter font-normal border rounded-xl outline-none transition-colors text-sm sm:text-base w-full px-4 h-6 sm:h-8 py-2.5 sm:py-4';

  const variants = {
    default:
      'border-text-secondary text-text-primary placeholder-text-placeholder hover:border-border focus:border-border focus:ring focus:ring-border',
    error:
      'border-error text-error placeholder-error/60 hover:border-error focus:border-error focus:ring focus:ring-error/20 bg-error/5',
    success:
      'border-success text-success placeholder-success/60 hover:border-success focus:border-success focus:ring focus:ring-success/20 bg-success/5',
  };

  return (
    <div className="w-full">
      <input
        className={`${baseStyles} ${variants[variant]} ${className}`}
        {...props}
      />
    </div>
  );
};
