import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/apiService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar si hay token almacenado al cargar la aplicación
    const token = localStorage.getItem('access_token');
    if (token) {
      apiService.setAuthToken(token);
      setIsAuthenticated(true);
      // Aquí podrías hacer una llamada para obtener datos del usuario
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await apiService.login(email, password);
      const { access, refresh, user: userData } = response.data;
      
      // Guardar tokens en localStorage
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      // Configurar token en el servicio API
      apiService.setAuthToken(access);
      
      // Actualizar estado
      setIsAuthenticated(true);
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('Error en login:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error de autenticación' 
      };
    }
  };

  const logout = () => {
    // Limpiar tokens
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Limpiar token del servicio API
    apiService.setAuthToken(null);
    
    // Actualizar estado
    setIsAuthenticated(false);
    setUser(null);
  };

  const value = {
    isAuthenticated,
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
};