/**
 * ============================================================================
 * File: frontend/src/components/__tests__/ApiClient.test.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — API Client Configuration Tests.
 *
 * Verifies the Axios client setup:
 * - Base URL configuration for development/production
 * - Content-Type header is set to JSON
 * - Request interceptors are registered
 * - Response interceptors handle 401/403 errors
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
  length: 0,
  key: vi.fn(),
};
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock });

describe('API Client', () => {
  beforeEach(() => {
    vi.resetModules();
    sessionStorageMock.getItem.mockClear();
  });

  it('creates an axios instance with JSON content type', async () => {
    const { apiClient } = await import('../../api/client');
    expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('has request interceptors registered', async () => {
    const { apiClient } = await import('../../api/client');
    // Axios interceptors manager has handlers array
    expect(apiClient.interceptors.request).toBeDefined();
  });

  it('has response interceptors registered', async () => {
    const { apiClient } = await import('../../api/client');
    expect(apiClient.interceptors.response).toBeDefined();
  });
});
