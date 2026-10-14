// ==========================================
//
// Description: Login Page
//
// File: LoginPage.jsx
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

import AuthTemplate from '../../components/templates/auth_layout/AuthTemplate';
import { LoginForm } from '../../components/organisms/login_form/LoginForm';
import { loginPageLogic } from './loginPageLogic';
import { loginFormLogic } from '../../components/organisms/login_form/loginFormLogic';
import { useCallback } from 'react';
import { LoadingSpinner } from '../../components/atoms/spinner/LoadingSpinner';

export default function LoginPage() {
  // Page business logic
  const { handleLogin, isLoading } = loginPageLogic();

  // Form business logic
  const formLogic = loginFormLogic();

  // Handle form submission
  const handleFormSubmit = useCallback(() => {
    if (formLogic.canSubmit) {
      formLogic.setIsSubmitting(true);
      handleLogin(formLogic.formData).finally(() => {
        formLogic.setIsSubmitting(false);
      });
    }
  }, [formLogic.canSubmit, formLogic.formData, handleLogin]);

  if (isLoading) {
    return (
      <AuthTemplate>
        <LoadingSpinner message="Loading..." />
      </AuthTemplate>
    );
  }

  return (
    <AuthTemplate>
      <LoginForm
        // Form state
        formData={formLogic.formData}
        errors={formLogic.errors}
        touched={formLogic.touched}
        isSubmitting={formLogic.isSubmitting}
        canSubmit={formLogic.canSubmit}
        // Form actions
        createFieldHandlers={formLogic.createFieldHandlers}
        onSubmit={handleFormSubmit}
      />
    </AuthTemplate>
  );
}
