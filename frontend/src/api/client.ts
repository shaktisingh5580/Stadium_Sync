/**
 * ===============================================================================
 * File: frontend/src/api/client.ts
 * Purpose: Axios HTTP client configuration - sets base URL, request/response 
 *          interceptors, JWT token auto-injection, error handling.
 * Architecture: Creates Axios instance with interceptors: request adds 
 *               Authorization header from sessionStorage; response handles 401 
 *               (token expired) by triggering refresh/logout.
 * Inputs: VITE_API_URL environment variable, JWT token from sessionStorage.
 * Outputs: Configured Axios instance for API calls with auto-token management.
 * Hackathon Vertical: Security & Authentication
 * ===============================================================================
 */

import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || (
  import.meta.env.PROD ? '/api/v1' : 'http://localhost:8000/api/v1'
);

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/** Retrieve the JWT token for Authorization header injection. */
function getAuthHeaders(): Record<string, string> {
  const token = sessionStorage.getItem('stadium_sync_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Clear all auth state from sessionStorage. */
export function clearAuthenticatedSession(): void {
  sessionStorage.removeItem('stadium_sync_token');
  sessionStorage.removeItem('stadium_sync_auth_provider');
}

// Interceptor to attach JWT token to every request
apiClient.interceptors.request.use(async (config) => {
  const authHeaders = getAuthHeaders();
  for (const [key, value] of Object.entries(authHeaders)) {
    if (value) {
      config.headers.set(key, value);
    }
  }
  return config;
});

// Interceptor to handle expired tokens
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.warn("Token expired or unauthorized. Clearing session.");
      clearAuthenticatedSession();
      window.location.reload();
    }
    return Promise.reject(error);
  }
);
