import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import api from '../api/client';

interface AuthState {
  token: string | null;
  patientId: string | null;
  username: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

interface AuthContextValue extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
}

export interface RegisterData {
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  blood_type?: string;
  allergies?: { substance: string; reaction?: string; severity?: string }[];
  family_history?: string[];
}

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = 'aibolit_token';
const PATIENT_KEY = 'aibolit_patient_id';
const USERNAME_KEY = 'aibolit_username';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    token: null,
    patientId: null,
    username: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Validate stored token on mount
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setState(s => ({ ...s, isLoading: false }));
      return;
    }

    api.get('/auth/me', { headers: { Authorization: `Bearer ${token}` } })
      .then(({ data }) => {
        setState({
          token,
          patientId: data.patient_id,
          username: data.username,
          isAuthenticated: true,
          isLoading: false,
        });
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(PATIENT_KEY);
        localStorage.removeItem(USERNAME_KEY);
        setState({ token: null, patientId: null, username: null, isAuthenticated: false, isLoading: false });
      });
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const { data } = await api.post('/auth/login', { username, password });
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(PATIENT_KEY, data.patient_id);
    localStorage.setItem(USERNAME_KEY, data.username);
    setState({
      token: data.token,
      patientId: data.patient_id,
      username: data.username,
      isAuthenticated: true,
      isLoading: false,
    });
  }, []);

  const register = useCallback(async (regData: RegisterData) => {
    const { data } = await api.post('/auth/register', regData);
    localStorage.setItem(TOKEN_KEY, data.token);
    localStorage.setItem(PATIENT_KEY, data.patient_id);
    localStorage.setItem(USERNAME_KEY, data.username);
    setState({
      token: data.token,
      patientId: data.patient_id,
      username: data.username,
      isAuthenticated: true,
      isLoading: false,
    });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(PATIENT_KEY);
    localStorage.removeItem(USERNAME_KEY);
    setState({ token: null, patientId: null, username: null, isAuthenticated: false, isLoading: false });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
