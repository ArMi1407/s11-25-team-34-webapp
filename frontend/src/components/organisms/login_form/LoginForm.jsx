// ==========================================
//
// Description: Login Form
//
// File: LoginForm.jsx
// Author: Anthony Bañon
// Created: 2025-11-22
// Last Updated: 2025-11-22
// ==========================================

import { PasswordInput } from '../../molecules/inputs/PasswordInput';
import { UsernameInput } from '../../molecules/inputs/UsernameInput';
import { SignInButton } from '../../molecules/buttons/SignInButton';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';
import { Link } from '../../atoms/link/Link';
import { ErrorMessage } from '../../atoms/text/ErrorMessage';

export const LoginForm = ({
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
    <div className="w-full flex flex-col justify-center h-62 sm:h-84 px-8 sm:px-16 md:px-22 lg:px-24 xl:px-26">
      <form onSubmit={handleSubmit} noValidate>
        <Title variant="subtitle" className="mb-4 sm:mb-6 text-center">
          Login
        </Title>

        <div className="flex flex-col gap-2 sm:gap-3">
          {/* Username Field */}
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

          {/* Password Field */}
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

          {/* Submit Button */}
          <SignInButton
            type="submit"
            disabled={!canSubmit}
            isLoading={isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Login'}
          </SignInButton>
        </div>

        {/* Sign Up Link */}
        <div className="mt-1.5 md:mt-2 flex justify-between">
          <Paragraph className="text-xs md:text-sm text-text-secondary">
            ¿No tienes una cuenta?
          </Paragraph>
          <Link
            to="/register"
            variant="secondary"
            className="text-xs md:text-sm"
          >
            Regístrate
          </Link>
        </div>
      </form>
    </div>
  );
};
