/**
 * ============================================================================
 * File: frontend/src/api/client.ts
 * Purpose: Axios HTTP Client Configuration.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Configured Axios instance for all API calls.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Axios HTTP Client Configuration.
 *
 * Creates a pre-configured Axios instance that:
 * - Points to the FastAPI backend (auto-detects dev vs. production via VITE_API_URL).
 * - Attaches the JWT Bearer token to every outgoing request.
 * - Automatically clears the session and reloads on 401/403 responses (expired tokens).
 *
 * This module is the single source of truth for all API calls in the frontend.
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
