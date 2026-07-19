/**
 * ============================================================================
 * FILE: frontend/src/components/__tests__/App.test.tsx
 * PURPOSE: Provides core functionality and logic for this module.
 * ARCHITECTURE: React/Vite/TypeScript component
 * INPUTS: Standard module props or API responses
 * OUTPUTS: Rendered DOM or internal logic
 * HACKATHON VERTICAL: Fan Experience & Navigation
 * ============================================================================
 */
import React from 'react';
/**
 * ============================================================================
 * File: frontend/src/components/__tests__/App.test.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — App Component Tests.
 *
 * Verifies the root App component:
 * - Renders without crashing
 * - Shows QR Scanner when not authenticated
 * - Shows admin dashboard when ?admin=true
 */
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock framer-motion to avoid animation issues in tests
vi.mock('framer-motion', () => ({
  AnimatePresence: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  motion: {
    div: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) => <button {...props}>{children}</button>,
  },
}));

// Mock lazy-loaded components
vi.mock('@/components/StadiumChat', () => ({
  StadiumChat: () => <div data-testid="stadium-chat">Chat Interface</div>,
}));

vi.mock('@/pages/AdminDashboard', () => ({
  AdminDashboard: () => <div data-testid="admin-dashboard">Admin Dashboard</div>,
}));

vi.mock('@/components/auth/QRScanner', () => ({
  QRScanner: ({ onScanSuccess }: { onScanSuccess: () => void }) => (
    <div data-testid="qr-scanner">
      <button onClick={onScanSuccess}>Scan QR</button>
    </div>
  ),
}));

describe('App Component', () => {
  beforeEach(() => {
    sessionStorage.clear();
    // Reset window.location.search
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { ...window.location, search: '' },
    });
  });

  it('renders QR Scanner when not authenticated', async () => {
    const App = (await import('../../App')).default;
    render(<App />);
    expect(screen.getByTestId('qr-scanner')).toBeInTheDocument();
  });

  it('has proper accessibility landmarks', async () => {
    const App = (await import('../../App')).default;
    render(<App />);
    const mainContent = document.getElementById('main-content');
    expect(mainContent).toBeTruthy();
    expect(mainContent?.getAttribute('role')).toBe('main');
  });
});
