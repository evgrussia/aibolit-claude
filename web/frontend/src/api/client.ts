import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// Attach auth token to every request
api.interceptors.request.use(config => {
  const token = localStorage.getItem('aibolit_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize error messages + handle 401
api.interceptors.response.use(
  res => res,
  err => {
    if (err.code === 'ECONNABORTED') throw new Error('Превышено время ожидания. Проверьте подключение к серверу.');
    if (!err.response) throw new Error('Сервер недоступен. Убедитесь, что backend запущен.');
    // On 401, clear token and redirect to login
    if (err.response.status === 401) {
      localStorage.removeItem('aibolit_token');
      localStorage.removeItem('aibolit_patient_id');
      localStorage.removeItem('aibolit_username');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    const detail = err.response?.data?.detail;
    throw new Error(detail || `Ошибка ${err.response.status}`);
  }
);

export default api;
