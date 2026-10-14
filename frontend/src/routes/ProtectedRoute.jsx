// ==========================================
//
// Description: Protected Route Component
// Adaptado para Django UserProfile y BrandProfile
//
// File: ProtectedRoute.jsx
// Author: Anthony Bañon
// Created: 2025-12-09
// Last Updated: 2025-12-09
// ==========================================

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ROUTES } from '../utils/constants';

export const ProtectedRoute = ({
  children,
  requiredRole = null,
  requiredBrandManager = false,
  redirectTo = ROUTES.LOGIN,
  unauthorizedRedirect = ROUTES.HOME,
}) => {
  const { isAuthenticated, loading, user } = useAuth();

  // Mostrar spinner mientras carga
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Si no está autenticado, redirigir al login
  if (!isAuthenticated) {
    // Guardar la ruta actual para redirigir después del login
    const currentPath = window.location.pathname + window.location.search;
    if (currentPath !== ROUTES.LOGIN) {
      localStorage.setItem('return_url', currentPath);
    }

    return <Navigate to={redirectTo} replace />;
  }

  // Determinar el rol del usuario según la estructura de Django
  const getUserRole = () => {
    if (!user) return null;

    // Verificar si es brand manager
    if (user.is_brand_manager) {
      return 'brand_manager';
    }

    // Si tiene brand_profile también es brand manager
    if (user.brand_profile) {
      return 'brand_manager';
    }

    // Usuario regular
    return 'regular_user';
  };

  const userRole = getUserRole();

  // Verificar si se requiere ser brand manager
  if (requiredBrandManager) {
    if (!user?.is_brand_manager && !user?.brand_profile) {
      console.warn('Acceso denegado: Se requiere ser brand manager');
      return <Navigate to={unauthorizedRedirect || '/unauthorized'} replace />;
    }
  }

  // Verificar rol específico si se requiere
  if (requiredRole) {
    if (userRole !== requiredRole) {
      console.warn(
        `Acceso denegado: Se requiere rol ${requiredRole}, usuario tiene rol ${userRole}`
      );
      return <Navigate to={unauthorizedRedirect || '/unauthorized'} replace />;
    }
  }

  // Si todo está bien, renderizar los children
  return children;
};

// Versión más simple compatible con tu anterior ProtectedRoute
export const SimpleProtectedRoute = ({
  children,
  requiredRole,
  redirectTo = ROUTES.LOGIN,
}) => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  // Determinar rol para la versión simple
  const getUserRole = () => {
    if (!user) return null;

    if (user.is_brand_manager || user.brand_profile) {
      return 'brand_manager';
    }

    return 'regular_user';
  };

  const userRole = getUserRole();

  if (requiredRole && userRole !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

export default ProtectedRoute;
