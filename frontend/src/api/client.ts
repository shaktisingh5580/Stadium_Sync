import axios from 'axios';

// Get API base URL from env or use default localhost port for FastAPI
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach JWT token to every request
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('stadium_sync_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle expired tokens
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.warn("Token expired or unauthorized. Clearing session.");
      localStorage.removeItem('stadium_sync_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);
