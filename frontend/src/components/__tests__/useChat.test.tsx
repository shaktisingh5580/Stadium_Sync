/**
 * ============================================================================
 * File: frontend/src/components/__tests__/useChat.test.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — useChat Hook Tests.
 *
 * Verifies the chat state management hook:
 * - Initializes with empty messages
 * - Returns expected interface (messages, sendMessage, isLoading)
 * - Manages loading state correctly
 */
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the sendChatMessage API
vi.mock('@/api', () => ({
  sendChatMessage: vi.fn().mockResolvedValue({
    message: 'Hello! Welcome to Stadium Sync.',
    ui_action: 'NONE',
    payload: null,
  }),
}));

describe('useChat Hook', () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.clearAllMocks();
  });

  it('initializes with empty messages', async () => {
    const { useChat } = await import('../../hooks/useChat');
    const { result } = renderHook(() => useChat());
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
  });

  it('returns the expected interface', async () => {
    const { useChat } = await import('../../hooks/useChat');
    const { result } = renderHook(() => useChat());
    expect(result.current).toHaveProperty('messages');
    expect(result.current).toHaveProperty('sendMessage');
    expect(result.current).toHaveProperty('addMessage');
    expect(result.current).toHaveProperty('isLoading');
  });

  it('addMessage appends to the message list', async () => {
    const { useChat } = await import('../../hooks/useChat');
    const { result } = renderHook(() => useChat());

    act(() => {
      result.current.addMessage({
        role: 'system',
        content: 'Welcome to Stadium Sync!',
      });
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].content).toBe('Welcome to Stadium Sync!');
    expect(result.current.messages[0].role).toBe('system');
  });
});
