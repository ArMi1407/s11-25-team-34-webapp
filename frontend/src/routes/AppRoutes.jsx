// ==========================================
//
// Description: App Routes
//
// File: AppRoutes.jsx
// Author: Anthony Bañon
// Created: 2025-11-24
// Last Updated: 2025-11-24
// ==========================================

import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
// Pages
import CartPage from '../pages/cart/CartPage';
import HomePage from '../pages/home/HomePage';
import ProfilePage from '../pages/profile/ProfilePage';
import LoginPage from '../pages/login/LoginPage';
import UnauthorizedPage from '../pages/auth/Unauthorized';
import RegisterPage from '../pages/register/RegisterPage';
// // Action Wrappers
import { ProtectedRoute } from './ProtectedRoute';
import { SignupRoute } from './SignupRoute';

export const AppRoutes = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route
        path="/profile"
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
    </Routes>
  );
};
