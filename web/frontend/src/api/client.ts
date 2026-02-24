import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

const TOKEN_KEY = 'aibolit_token';
const REFRESH_KEY = 'aibolit_refresh_token';
const PATIENT_KEY = 'aibolit_patient_id';
const USERNAME_KEY = 'aibolit_username';

let isRefreshing = false;
let refreshSubscribers: { resolve: (token: string) => void; reject: (err: unknown) => void }[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach(s => s.resolve(token));
  refreshSubscribers = [];
}

function onRefreshFailed(err: unknown) {
  refreshSubscribers.forEach(s => s.reject(err));
  refreshSubscribers = [];
}

// Attach auth token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize error messages + handle 401 with auto-refresh
api.interceptors.response.use(
  res => res,
  async err => {
    if (err.code === 'ECONNABORTED') throw new Error('Превышено время ожидания. Проверьте подключение к серверу.');
    if (!err.response) throw new Error('Сервер недоступен. Убедитесь, что backend запущен.');

    const originalRequest = err.config;

    // On 401, try to refresh the token (skip for auth endpoints)
    if (err.response.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/')) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem(REFRESH_KEY);

      if (!refreshToken) {
        clearAuth();
        return Promise.reject(err);
      }

      if (isRefreshing) {
        // Wait for the refresh to complete
        return new Promise((resolve, reject) => {
          refreshSubscribers.push({
            resolve: (newToken: string) => {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              resolve(api(originalRequest));
            },
            reject,
          });
        });
      }

      isRefreshing = true;
      try {
        const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
        localStorage.setItem(TOKEN_KEY, data.token);
        localStorage.setItem(REFRESH_KEY, data.refresh_token);
        isRefreshing = false;
        onRefreshed(data.token);
        originalRequest.headers.Authorization = `Bearer ${data.token}`;
        return api(originalRequest);
      } catch {
        isRefreshing = false;
        onRefreshFailed(err);
        clearAuth();
        return Promise.reject(err);
      }
    }

    const detail = err.response?.data?.detail;
    throw new Error(detail || `Ошибка ${err.response.status}`);
  }
);

function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(PATIENT_KEY);
  localStorage.removeItem(USERNAME_KEY);
  if (window.location.pathname !== '/login') {
    window.location.href = '/login';
  }
}

export default api;
