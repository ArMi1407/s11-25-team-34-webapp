// ==========================================
//
// Description: Text Component
//
// File: Text.jsx
// Author: Anthony Bañon
// Created: 2025-11-09
// Last Updated: 2025-11-09
// ==========================================

export const Paragraph = ({
  children,
  variant = 'normal',
  className = '',
  ...props
}) => {
  // Define variant styles
  const variants = {
    normal: 'font-normal font-roboto',
    semibold: 'font-semibold font-roboto',
    bold: 'font-bold font-roboto',
  };

  return (
    <span className={`${variants[variant]} ${className}`} {...props}>
      {children}
    </span>
  );
};
