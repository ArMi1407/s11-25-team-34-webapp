// ==========================================
//
// Description: Sustainability Story Input Component
//
// File: SustainabilityStoryInput.jsx
// Author: Anthony Bañon
// Created: 2025-11-29
// Last Updated: 2025-11-29
// ==========================================

export const SustainabilityStoryInput = ({ hasError, ...props }) => {
  const variantClass = hasError
    ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
    : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500';

  return (
    <div className="w-full">
      <textarea
        className={`w-full p-3 border rounded-lg focus:outline-none focus:ring-1 ${variantClass}`}
        placeholder="Sustainability Story (Optional)"
        rows="4"
        {...props}
      />
    </div>
  );
};
