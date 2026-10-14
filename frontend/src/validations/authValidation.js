// validations/authValidation.js
// Frontend validations for auth forms

// Validation rules
// validations/authValidation.js
// Frontend validations for auth forms

// Validation rules (consistentes con backend)
const USERNAME_REGEX = /^[a-zA-Z0-9_]{3,20}$/;
const PASSWORD_MIN_LENGTH = 6;
const PASSWORD_MAX_LENGTH = 255;

// Validation functions - ESTANDARIZADAS A NULL
export const validateUsername = (username) => {
  if (!username) return 'Username is required';
  if (username.length < 3) return 'Username must be at least 3 characters';
  if (username.length > 20) return 'Username cannot exceed 20 characters';
  if (!USERNAME_REGEX.test(username))
    return 'Username can only contain letters, numbers and underscore';
  return null; // ← Cambiado a null
};

export const validatePassword = (password) => {
  if (!password) return 'Password is required';
  if (password.length < PASSWORD_MIN_LENGTH)
    return `Password must be at least ${PASSWORD_MIN_LENGTH} characters`;
  if (password.length > PASSWORD_MAX_LENGTH)
    return `Password cannot exceed ${PASSWORD_MAX_LENGTH} characters`;
  return null; // ← Cambiado a null
};

export const validateCurrentPassword = (currentPassword) => {
  if (!currentPassword) return 'Current password is required';
  return null; // ← Cambiado a null
};

export const validateNewPassword = (newPassword, currentPassword = '') => {
  if (!newPassword) return 'New password is required';
  if (newPassword.length < PASSWORD_MIN_LENGTH)
    return `New password must be at least ${PASSWORD_MIN_LENGTH} characters`;
  if (newPassword.length > PASSWORD_MAX_LENGTH)
    return `New password cannot exceed ${PASSWORD_MAX_LENGTH} characters`;
  if (newPassword === currentPassword)
    return 'New password must be different from current password';
  return null; // ← Cambiado a null
};

// export const validateRefreshToken = (refreshToken) => {
//   if (!refreshToken) return 'Refresh token is required';
//   // Basic JWT format validation (3 parts separated by dots)
//   const jwtParts = refreshToken.split('.');
//   if (jwtParts.length !== 3) return 'Invalid refresh token format';
//   return null; // ← Cambiado a null
// };

export const validateToken = (token) => {
  if (!token) return 'Token is required';
  return null; // ← Cambiado a null
};

// Complete form validations
export const validateLoginForm = (formData) => {
  const errors = {
    username: validateUsername(formData.username),
    password: validatePassword(formData.password),
  };

  // Filtrar solo errores reales (no null)
  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== null)
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

export const validateChangePasswordForm = (formData) => {
  const errors = {
    currentPassword: validateCurrentPassword(formData.currentPassword),
    newPassword: validateNewPassword(
      formData.newPassword,
      formData.currentPassword
    ),
  };

  // Filtrar solo errores reales (no null)
  const filteredErrors = Object.fromEntries(
    Object.entries(errors).filter(([_, value]) => value !== null)
  );

  const isValid = Object.keys(filteredErrors).length === 0;

  return { errors: filteredErrors, isValid };
};

// Individual field validation (for real-time validation)
export const validateAuthField = (fieldName, value, formData = {}) => {
  const validators = {
    username: validateUsername,
    password: validatePassword,
    currentPassword: validateCurrentPassword,
    newPassword: () => validateNewPassword(value, formData.currentPassword),
    // refreshToken: validateRefreshToken,
    token: validateToken,
  };

  if (!validators[fieldName]) {
    return null;
  }

  return validators[fieldName](value);
};
