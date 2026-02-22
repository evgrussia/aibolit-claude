import api from './client';
import type { RegisterData } from '../contexts/AuthContext';

interface AuthResponse {
  token: string;
  patient_id: string;
  username: string;
}

interface MeResponse {
  user_id: number;
  username: string;
  patient_id: string | null;
}

export async function login(username: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post('/auth/login', { username, password });
  return data;
}

export async function register(regData: RegisterData): Promise<AuthResponse> {
  const { data } = await api.post('/auth/register', regData);
  return data;
}

export async function getMe(): Promise<MeResponse> {
  const { data } = await api.get('/auth/me');
  return data;
}

export async function changePassword(oldPassword: string, newPassword: string) {
  const { data } = await api.post('/auth/change-password', {
    old_password: oldPassword,
    new_password: newPassword,
  });
  return data;
}

export async function deleteAccount() {
  const { data } = await api.delete('/auth/me');
  return data;
}
