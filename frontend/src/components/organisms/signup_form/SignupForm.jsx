// ==========================================
//
// Description: Sign Up Form
//
// File: SignupForm.jsx
// Author: Anthony Bañon
// Created: 2025-11-22
// Last Updated: 2025-11-22
// ==========================================

import { PasswordInput } from '../../molecules/inputs/PasswordInput';
import { UsernameInput } from '../../molecules/inputs/UsernameInput';
import { ConfirmPasswordInput } from '../../molecules/inputs/ConfirmPasswordInput';
import { SignUpButton } from '../../molecules/buttons/SignUpButton';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';
import { ErrorMessage } from '../../atoms/text/ErrorMessage';
import { Link } from '../../atoms/link/Link';

export const SignupForm = ({
  formData,
  errors,
  touched,
  isSubmitting,
  canSubmit,
  createFieldHandlers,
  onSubmit,
}) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <div className="w-full flex flex-col justify-center h-82 sm:h-114 px-8 sm:px-16 md:px-22 lg:px-24 xl:px-26">
      <form onSubmit={handleSubmit} noValidate>
        <div className="mb-4 sm:mb-6 text-center">
          <Title variant="subtitle">Create Account</Title>
          <Paragraph className="text-xs md:text-sm text-center text-text-secondary">
            Choose how you'll sign in
          </Paragraph>
        </div>

        <div className="flex flex-col gap-2 sm:gap-3">
          <div>
            <UsernameInput
              value={formData.username}
              {...createFieldHandlers('username')}
              disabled={isSubmitting}
              hasError={touched.username && errors.username}
            />
            {touched.username && errors.username && (
              <ErrorMessage>{errors.username}</ErrorMessage>
            )}
          </div>
          <div>
            <PasswordInput
              value={formData.password}
              {...createFieldHandlers('password')}
              disabled={isSubmitting}
              hasError={touched.password && errors.password}
            />
            {touched.password && errors.password && (
              <ErrorMessage>{errors.password}</ErrorMessage>
            )}
          </div>
          <div>
            <ConfirmPasswordInput
              value={formData.confirmPassword}
              {...createFieldHandlers('confirmPassword')}
              disabled={isSubmitting}
              hasError={touched.confirmPassword && errors.confirmPassword}
            />
            {touched.confirmPassword && errors.confirmPassword && (
              <ErrorMessage>{errors.confirmPassword}</ErrorMessage>
            )}
          </div>

          <SignUpButton
            type="submit"
            disabled={!canSubmit || isSubmitting}
            isLoading={isSubmitting}
          >
            {isSubmitting ? 'Creating Account...' : 'Create Account'}
          </SignUpButton>
        </div>

        <div className="mt-1.5 md:mt-2 flex justify-between">
          <Paragraph className="text-xs md:text-sm text-text-secondary">
            Do you have an account?
          </Paragraph>
          <Link to="/login" variant="secondary" className="text-xs md:text-sm">
            Sign In
          </Link>
        </div>
      </form>
    </div>
  );
};
