import React, { createContext, useContext, useEffect, useState } from 'react';
import { apiClient, getAuthToken, setAuthToken, removeAuthToken, isTokenExpired, getUserFromToken } from '@/lib/api';

interface User {
  user_id: number;
  email: string;
}

interface AuthContextType {
  user: User | null;
  signUp: (email: string, password: string) => Promise<{ error: any }>;
  signIn: (email: string, password: string) => Promise<{ error: any }>;
  signOut: () => Promise<{ error: any }>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing token on mount
    const checkExistingAuth = () => {
      const token = getAuthToken();
      if (token && !isTokenExpired(token)) {
        const userData = getUserFromToken(token);
        setUser(userData);
      } else {
        removeAuthToken();
        setUser(null);
      }
      setLoading(false);
    };

    checkExistingAuth();
  }, []);

  const signUp = async (email: string, password: string) => {
    const { data, error } = await apiClient.signUp(email, password);
    if (!error && data?.token) {
      setAuthToken(data.token);
      const userData = getUserFromToken(data.token);
      setUser(userData);
    }
    return { error };
  };

  const signIn = async (email: string, password: string) => {
    const { data, error } = await apiClient.signIn(email, password);
    if (!error && data?.token) {
      setAuthToken(data.token);
      const userData = getUserFromToken(data.token);
      setUser(userData);
    }
    return { error };
  };

  const signOut = async () => {
    removeAuthToken();
    setUser(null);
    return { error: null };
  };

  const value = {
    user,
    signUp,
    signIn,
    signOut,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
