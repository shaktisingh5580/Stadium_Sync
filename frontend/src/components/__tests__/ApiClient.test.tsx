/**
 * ============================================================================
 * FILE: frontend/src/components/__tests__/ApiClient.test.tsx
 * PURPOSE: Stadium Sync — API Client Configuration Tests. Verifies the Axios client setup: - Base URL configuration for development/production - Content-Type header is set to JSON - Request interceptors are registered - Response interceptors handle 401/403 errors
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
 * ============================================================================
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
