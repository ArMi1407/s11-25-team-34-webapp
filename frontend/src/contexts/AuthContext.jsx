// ==========================================
//
// Description: Auth Context for Django Token Authentication
//
// File: AuthContext.jsx
// Author: Anthony Bañon
// Created: 2025-12-09
// Last Updated: 2025-12-09
// Changes: Adaptado para Django Token Authentication
// ==========================================

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from 'react';
import { authService } from '../services/auth/authService';
import { tokenInterceptor } from '../services/auth/tokenInterceptor';
import { STORAGE_KEYS, ERROR_MESSAGES, ROUTES } from '../utils/constants';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Estados iniciales desde localStorage
  const [token, setToken] = useState(
    localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) || null
  );

  const [user, setUser] = useState(() => {
    const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    return userData ? JSON.parse(userData) : null;
  });

  const [loading, setLoading] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);

  const isAuthenticated = !!token;

  // Efecto para sincronizar cambios de estado con localStorage
  useEffect(() => {
    if (token) {
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token);
    } else {
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
    } else {
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    }
  }, [user]);

  // Inicializar token interceptor y verificar autenticación al cargar
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Configurar interceptor
        tokenInterceptor.setAuthFunctions({
          logout: handleLogout,
        });

        // Configurar interceptor en axios (si estás usando axios en authService)
        // Nota: tu api.js ya maneja los tokens automáticamente con fetch

        // Verificar autenticación inicial
        await checkAuth();
      } catch (error) {
        console.error('Error inicializando autenticación:', error);
      } finally {
        setLoading(false);
        setIsInitialized(true);
      }
    };

    initializeAuth();
  }, []);

  // Verificar autenticación al cargar la aplicación
  const checkAuth = useCallback(async () => {
    if (!token) {
      return;
    }

    try {
      // Intentar obtener el perfil para verificar si el token es válido
      await getProfile();
    } catch (error) {
      console.warn('Token inválido o expirado:', error);
      // El error 401 ya es manejado automáticamente por api.js y tokenInterceptor
    }
  }, [token]);

  // Obtener perfil del usuario
  const getProfile = useCallback(async () => {
    try {
      const response = await authService.getProfile();
      if (response.data) {
        setUser(response.data);
        return response.data;
      }
      return null;
    } catch (error) {
      throw error;
    }
  }, []);

  // Login
  const login = useCallback(async (username, password) => {
    try {
      setLoading(true);
      const result = await authService.login(username, password);

      if (result.data && result.data.token) {
        // Guardar token en estado
        setToken(result.data.token);

        // Guardar datos de usuario (sin el token)
        const userData = { ...result.data };
        delete userData.token;
        setUser(userData);

        return {
          success: true,
          data: result.data,
          user: userData,
        };
      }

      return {
        success: false,
        error: ERROR_MESSAGES.INVALID_CREDENTIALS,
      };
    } catch (error) {
      console.error('Login error:', error);
      return {
        success: false,
        error: error.message || ERROR_MESSAGES.INVALID_CREDENTIALS,
      };
    } finally {
      setLoading(false);
    }
  }, []);

  // Cambiar contraseña
  const changePassword = useCallback(async (currentPassword, newPassword) => {
    try {
      const result = await authService.changePassword(
        currentPassword,
        newPassword
      );
      return { success: true, data: result.data };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Error al cambiar contraseña',
      };
    }
  }, []);

  // Logout
  const handleLogout = useCallback(async () => {
    try {
      // Intentar llamar al endpoint de logout
      await authService.logout();
    } catch (error) {
      console.warn('Logout API call failed:', error);
      // Continuar con el logout local incluso si falla la llamada al servidor
    } finally {
      // Limpiar estados
      setToken(null);
      setUser(null);

      // Limpiar localStorage
      localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);

      // Redirigir a login
      window.location.href = ROUTES.LOGIN;
    }
  }, []);

  // Función para forzar logout (sin llamar a la API)
  const forceLogout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.USER_DATA);
    window.location.href = ROUTES.LOGIN;
  }, []);

  // Actualizar datos del usuario
  const updateUser = useCallback((userData) => {
    setUser((prevUser) => ({
      ...prevUser,
      ...userData,
    }));
  }, []);

  // Obtener token actual
  const getCurrentToken = useCallback(() => {
    return token || localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
  }, [token]);

  // Valor del contexto
  const value = {
    // Estados
    token,
    user,
    isAuthenticated,
    loading,
    isInitialized,

    // Métodos
    login,
    logout: handleLogout,
    forceLogout,
    changePassword,
    getProfile,
    updateUser,
    getCurrentToken,

    // Helpers para roles y permisos (adaptados para Django)
    getUserRole: () => {
      if (!user) return null;

      // Brand manager si is_brand_manager es true o tiene brand_profile
      if (user.is_brand_manager || user.brand_profile) {
        return 'brand_manager';
      }

      return 'regular_user';
    },

    // Métodos de conveniencia
    isBrandManager: () => {
      return user?.is_brand_manager || !!user?.brand_profile;
    },

    isRegularUser: () => {
      return !user?.is_brand_manager && !user?.brand_profile;
    },

    hasRole: (role) => {
      if (!user) return false;

      const userRole =
        user.is_brand_manager || user.brand_profile
          ? 'brand_manager'
          : 'regular_user';

      return userRole === role;
    },

    // Para compatibilidad con tu código anterior
    get role() {
      if (!user) return null;
      return user.is_brand_manager || user.brand_profile
        ? 'brand_manager'
        : 'regular_user';
    },

    //
    hasPermission: (permission) => {
      return user?.permissions?.includes(permission);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook personalizado para usar el contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de un AuthProvider');
  }
  return context;
};

// Hook para proteger rutas
export const useProtectedRoute = (
  requiredRole = null,
  requiredPermission = null
) => {
  const { isAuthenticated, loading, user, forceLogout } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      // Guardar la ruta actual para redirigir después del login
      const currentPath = window.location.pathname + window.location.search;
      if (currentPath !== ROUTES.LOGIN) {
        localStorage.setItem('return_url', currentPath);
      }

      // Redirigir a login
      window.location.href = ROUTES.LOGIN;
      return;
    }

    if (!loading && isAuthenticated) {
      // Verificar rol si se requiere
      if (requiredRole && user?.role !== requiredRole) {
        console.warn('Usuario no tiene el rol requerido');
        forceLogout();
        return;
      }

      // Verificar permiso si se requiere
      if (
        requiredPermission &&
        !user?.permissions?.includes(requiredPermission)
      ) {
        console.warn('Usuario no tiene el permiso requerido');
        forceLogout();
        return;
      }
    }
  }, [
    isAuthenticated,
    loading,
    user,
    requiredRole,
    requiredPermission,
    forceLogout,
  ]);

  return { isAuthenticated, loading, user };
};
