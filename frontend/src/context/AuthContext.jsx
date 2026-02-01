import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [credentials, setCredentials] = useState(localStorage.getItem('credentials') || null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (credentials) {
        try {
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
        } catch (error) {
          console.error('Failed to fetch user:', error);
          logout();
        }
      }
      setLoading(false);
    };
    
    checkAuth();
  }, [credentials]);

  const login = async (email, password) => {
    console.log('AuthContext.login called with:', email);
    try {
      const response = await authAPI.login({ email, password });
      console.log('Login response:', response.data);
      const { user } = response.data;
      
      // Store email:password as credentials
      const creds = `${email}:${password}`;
      localStorage.setItem('credentials', creds);
      console.log('Credentials stored:', creds);
      setCredentials(creds);
      setUser(user);
      
      return user;
    } catch (error) {
      console.error('Login failed in AuthContext:', error);
      throw error;
    }
  };

  const register = async (name, email, password) => {
    console.log('AuthContext.register called with:', { name, email });
    try {
      const response = await authAPI.register({ name, email, password });
      console.log('Register response:', response.data);
      const { user } = response.data;
      
      // Store email:password as credentials
      const creds = `${email}:${password}`;
      localStorage.setItem('credentials', creds);
      console.log('Credentials stored:', creds);
      setCredentials(creds);
      setUser(user);
      
      return user;
    } catch (error) {
      console.error('Register failed in AuthContext:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('credentials');
    setCredentials(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, credentials, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
