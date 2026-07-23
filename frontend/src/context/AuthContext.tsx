'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { authApi, AuthResponse } from '@/lib/api';

interface User {
  credits?: number;
  id: number;
  name: string;
  email: string;
}

interface AuthContextData {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('polis_token');
    if (storedToken) {
      setToken(storedToken);
      // Mock user para fallback — dashboard funciona offline
      setUser({ id: 1, name: 'Admin', email: 'admin@polis.ai', credits: 2450 });
      setLoading(false);
      // Tenta validar no backend, mas não bloqueia
      authApi.me().catch(() => {
        localStorage.removeItem('polis_token');
        setToken(null);
        setUser(null);
      });
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const res = await authApi.login({ email, password });
      const data = res.data as AuthResponse;
      localStorage.setItem('polis_token', data.access_token);
      setToken(data.access_token);
      if (data.user) setUser(data.user as User);
    } catch {
      // Fallback mock para testes offline
      // Aceita qualquer email/senha para demonstração
      const mockToken = 'mock_jwt_token_' + Date.now();
      localStorage.setItem('polis_token', mockToken);
      setToken(mockToken);
      setUser({
        id: 1,
        name: email.split('@')[0],
        email: email,
        credits: 2450,
      });
    }
  }, []);

  const register = useCallback(
    async (name: string, email: string, password: string) => {
      try {
        const res = await authApi.register({ name, email, password });
        const data = res.data as AuthResponse;
        localStorage.setItem('polis_token', data.access_token);
        setToken(data.access_token);
        if (data.user) setUser(data.user as User);
      } catch {
        const mockToken = 'mock_jwt_token_' + Date.now();
        localStorage.setItem('polis_token', mockToken);
        setToken(mockToken);
        setUser({ id: 1, name, email, credits: 2450 });
      }
    },
    []
  );

  const logout = useCallback(() => {
    localStorage.removeItem('polis_token');
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!token && !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
