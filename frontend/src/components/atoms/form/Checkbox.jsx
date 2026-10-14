// ==========================================
//
// Description: Checkbox Component
//
// File: Checkbox.jsx
// Author: Anthony Bañon
// Created: 2025-11-29
// Last Updated: 2025-11-29
// ==========================================

export const Checkbox = ({
  id,
  checked = false,
  onChange,
  onBlur,
  disabled = false,
  hasError = false,
  className = '',
  ...props
}) => {
  const handleChange = (event) => {
    if (onChange && !disabled) {
      onChange(event);
    }
  };

  const handleBlur = (event) => {
    if (onBlur && !disabled) {
      onBlur(event);
    }
  };

  return (
    <input
      id={id}
      type="checkbox"
      checked={checked}
      onChange={handleChange}
      onBlur={handleBlur}
      disabled={disabled}
      className={`
        h-4 
        w-4 
        rounded 
        border 
        ${hasError ? 'border-red-500' : 'border-gray-300'}
        ${hasError ? 'focus:border-red-500' : 'focus:border-blue-500'}
        ${hasError ? 'focus:ring-red-500' : 'focus:ring-blue-500'}
        ${
          disabled
            ? 'bg-gray-100 cursor-not-allowed opacity-60'
            : 'bg-white cursor-pointer'
        }
        text-blue-600 
        focus:ring-2 
        focus:ring-offset-0
        focus:outline-none
        ${className}
      `}
      {...props}
    />
  );
};
