// ==========================================
//
// Description: Register Form
//
// File: RegisterForm.jsx
// Author: Anthony Bañon
// Created: 2025-11-29
// Last Updated: 2025-11-29
// ==========================================

import { FirstNameInput } from '../../molecules/inputs/FirstNameInput';
import { LastNameInput } from '../../molecules/inputs/LastNameInput';
import { EmailInput } from '../../molecules/inputs/EmailInput';
import { PasswordInput } from '../../molecules/inputs/PasswordInput';
import { UsernameInput } from '../../molecules/inputs/UsernameInput';
import { ConfirmPasswordInput } from '../../molecules/inputs/ConfirmPasswordInput';
import { PhoneInput } from '../../molecules/inputs/PhoneInput'; // Nuevo input
import { BrandNameInput } from '../../molecules/inputs/BrandNameInput';
import { SustainabilityStoryInput } from '../../molecules/inputs/SustainabilityStoryInput';
import { SignUpButton } from '../../molecules/buttons/SignUpButton';
import { Title } from '../../atoms/text/Title';
import { Paragraph } from '../../atoms/text/Paragraph';
import { ErrorMessage } from '../../atoms/text/ErrorMessage';
import { Link } from '../../atoms/link/Link';
import { Checkbox } from '../../atoms/form/Checkbox'; // Si tienes checkbox

export const RegisterForm = ({
  formData,
  errors,
  touched,
  isSubmitting,
  canSubmit,
  createFieldHandlers,
  onSubmit,
  isBrandRegistration = false, // Nuevo prop opcional
}) => {
  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <div className="w-full flex flex-col justify-center h-82 sm:h-114 px-8 sm:px-16 md:px-22 lg:px-24 xl:px-26">
      <form onSubmit={handleSubmit} noValidate>
        <div className="mb-4 sm:mb-6 text-center">
          <Title variant="subtitle">
            {isBrandRegistration ? 'Create Brand Account' : 'Create Account'}
          </Title>
          <Paragraph className="text-xs md:text-sm text-center text-text-secondary">
            {isBrandRegistration
              ? 'Register your brand and share your sustainability story'
              : 'Tell us a little about you'}
          </Paragraph>
        </div>

        <div className="flex flex-col gap-2 sm:gap-3">
          {/* First Name Field */}
          <div>
            <FirstNameInput
              value={formData.first_name || ''}
              {...createFieldHandlers('first_name')}
              disabled={isSubmitting}
              hasError={touched.first_name && errors.first_name}
            />
            {touched.first_name && errors.first_name && (
              <ErrorMessage>{errors.first_name}</ErrorMessage>
            )}
          </div>

          {/* Last Name Field */}
          <div>
            <LastNameInput
              value={formData.last_name || ''}
              {...createFieldHandlers('last_name')}
              disabled={isSubmitting}
              hasError={touched.last_name && errors.last_name}
            />
            {touched.last_name && errors.last_name && (
              <ErrorMessage>{errors.last_name}</ErrorMessage>
            )}
          </div>

          {/* Email Field */}
          <div>
            <EmailInput
              value={formData.email || ''}
              {...createFieldHandlers('email')}
              disabled={isSubmitting}
              hasError={touched.email && errors.email}
            />
            {touched.email && errors.email && (
              <ErrorMessage>{errors.email}</ErrorMessage>
            )}
          </div>

          {/* Username Field */}
          <div>
            <UsernameInput
              value={formData.username || ''}
              {...createFieldHandlers('username')}
              disabled={isSubmitting}
              hasError={touched.username && errors.username}
            />
            {touched.username && errors.username && (
              <ErrorMessage>{errors.username}</ErrorMessage>
            )}
          </div>

          {/* Phone Field (Opcional) */}
          <div>
            <PhoneInput
              value={formData.phone || ''}
              {...createFieldHandlers('phone')}
              disabled={isSubmitting}
              hasError={touched.phone && errors.phone}
              label="Phone (Optional)"
            />
            {touched.phone && errors.phone && (
              <ErrorMessage>{errors.phone}</ErrorMessage>
            )}
          </div>

          {/* Password Field */}
          <div>
            <PasswordInput
              value={formData.password || ''}
              {...createFieldHandlers('password')}
              disabled={isSubmitting}
              hasError={touched.password && errors.password}
            />
            {touched.password && errors.password && (
              <ErrorMessage>{errors.password}</ErrorMessage>
            )}
          </div>

          {/* Confirm Password Field */}
          <div>
            <ConfirmPasswordInput
              value={formData.password_confirm || ''}
              {...createFieldHandlers('password_confirm')}
              disabled={isSubmitting}
              hasError={touched.password_confirm && errors.password_confirm}
            />
            {touched.password_confirm && errors.password_confirm && (
              <ErrorMessage>{errors.password_confirm}</ErrorMessage>
            )}
          </div>

          {/* Brand Name Field (solo para brand registration) */}
          {isBrandRegistration && (
            <div>
              <BrandNameInput
                value={formData.brand_name || ''}
                {...createFieldHandlers('brand_name')}
                disabled={isSubmitting}
                hasError={touched.brand_name && errors.brand_name}
              />
              {touched.brand_name && errors.brand_name && (
                <ErrorMessage>{errors.brand_name}</ErrorMessage>
              )}
            </div>
          )}

          {/* Sustainability Story Field (solo para brand registration) */}
          {isBrandRegistration && (
            <div>
              <SustainabilityStoryInput
                value={formData.sustainability_story || ''}
                {...createFieldHandlers('sustainability_story')}
                disabled={isSubmitting}
                hasError={
                  touched.sustainability_story && errors.sustainability_story
                }
              />
              {touched.sustainability_story && errors.sustainability_story && (
                <ErrorMessage>{errors.sustainability_story}</ErrorMessage>
              )}
            </div>
          )}

          {/* Brand Manager Checkbox (Opcional, podría ser hidden) */}
          {isBrandRegistration && (
            <div className="flex items-center">
              <Checkbox
                id="is_brand_manager"
                checked={formData.is_brand_manager || false}
                {...createFieldHandlers('is_brand_manager')}
                disabled={isSubmitting}
              />
              <label htmlFor="is_brand_manager" className="ml-2 text-sm">
                I am registering as a brand manager
              </label>
            </div>
          )}

          {/* Submit Button */}
          <SignUpButton
            type="submit"
            disabled={!canSubmit || isSubmitting}
            isLoading={isSubmitting}
          >
            {isSubmitting
              ? isBrandRegistration
                ? 'Creating Brand Account...'
                : 'Creating Account...'
              : isBrandRegistration
              ? 'Create Brand Account'
              : 'Create Account'}
          </SignUpButton>

          {/* Error general */}
          {errors._general && (
            <ErrorMessage className="text-center">
              {errors._general}
            </ErrorMessage>
          )}
        </div>

        {/* Links de navegación */}
        <div className="mt-1.5 md:mt-2 flex justify-between">
          <Paragraph className="text-xs md:text-sm text-text-secondary">
            {isBrandRegistration
              ? 'Already have a brand account?'
              : 'Already have an account?'}
          </Paragraph>
          <Link to="/login" variant="secondary" className="text-xs md:text-sm">
            Sign In
          </Link>
        </div>

        {/* Link para cambiar tipo de registro */}
        {!isBrandRegistration && (
          <div className="mt-2 text-center">
            <Paragraph className="text-xs md:text-sm text-text-secondary">
              Want to register a brand?
            </Paragraph>
            <Link
              to="/register/brand"
              variant="primary"
              className="text-xs md:text-sm font-medium"
            >
              Register as Brand
            </Link>
          </div>
        )}
      </form>
    </div>
  );
};
