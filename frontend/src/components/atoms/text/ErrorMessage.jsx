// ==========================================
//
// Description: Error Message
//
// File: ErrorMessage.jsx
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

export const ErrorMessage = ({ children, className = '' }) => {
  return (
    <p
      className={`mt-1 text-xs flex items-center gap-1 text-error ${className}`}
    >
      <span>⚠️</span>
      {children}
    </p>
  );
};
