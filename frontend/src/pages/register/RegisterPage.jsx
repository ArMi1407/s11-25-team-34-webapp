// ==========================================
//
// Description: Register Page
//
// File: RegisterPage.jsx
// Author: Anthony Bañon
// Created: 2025-11-21
// Last Updated: 2025-11-21
// ==========================================

import AuthTemplate from '../../components/templates/auth_layout/AuthTemplate';
import { RegisterForm } from '../../components/organisms/register_form/RegisterForm';
import { registerPageLogic } from './registerPageLogic';
import { registerFormLogic } from '../../components/organisms/register_form/registerFormLogic';
import { useCallback } from 'react';
import { LoadingSpinner } from '../../components/atoms/spinner/LoadingSpinner';

export default function RegisterPage() {
  // Page business logic
  const { handleRegister, isLoading } = registerPageLogic();

  // Form business logic
  const formLogic = registerFormLogic();

  // Handle form submission
  const handleFormSubmit = useCallback(() => {
    if (formLogic.canSubmit) {
      formLogic.setIsSubmitting(true);
      handleRegister(formLogic.formData).finally(() => {
        formLogic.setIsSubmitting(false);
      });
    }
  }, [formLogic.canSubmit, formLogic.formData, handleRegister]);

  if (isLoading) {
    return (
      <AuthTemplate>
        <LoadingSpinner message="Loading registration..." />
      </AuthTemplate>
    );
  }

  return (
    <AuthTemplate>
      <RegisterForm
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
