import React, { createContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';

// Define types
interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

// Create context
export const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
});

// Auth provider component
export const AuthProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Check if user is already logged in
  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      // Fetch user profile using token
      const response = await fetch('http://localhost:8000/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Authentication failed');
      }
      
      const userData = await response.json();
      setUser(userData);
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Login function
  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Create form data - IMPORTANT: FastAPI OAuth2 expects form data, not JSON
      const formData = new URLSearchParams();
      formData.append('username', username); // OAuth2 standard field name
      formData.append('password', password);

      const response = await fetch('http://localhost:8000/api/v1/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded', // CHANGED: use form urlencoded
        },
        body: formData.toString(), // CHANGED: send as form data
      });

      if (!response.ok) {
        let errorMsg = 'Login failed';
        try {
          const errorData = await response.json();
          errorMsg = errorData.detail || errorMsg;
        } catch (e) {
          // If JSON parsing fails, use status text
          errorMsg = `${errorMsg}: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      
      // Store user data if available in response
      if (data.user) {
        setUser(data.user);
      } else {
        // Otherwise fetch user profile
        await checkAuth();
      }
      
      navigate('/dashboard');
    } catch (error: any) {
      console.error('Login error:', error);
      setError(error.message || 'Login failed');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/login');
  };

  // Check authentication when component mounts
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Context value
  const contextValue: AuthContextType = {
    user,
    isLoading,
    error,
    isAuthenticated: !!user,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};