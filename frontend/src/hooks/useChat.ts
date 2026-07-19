/**
 * ============================================================================
 * File: frontend/src/hooks/useChat.ts
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Chat State Hook (useChat).
 *
 * Manages the conversational state between the fan and the Gemini AI concierge:
 * - Persists chat history to sessionStorage for session continuity.
 * - Sends messages to the /chat endpoint with full conversation history for context.
 * - Handles Gemini's UI action directives (SHOW_MAP, SHOW_ROUTE, etc.) which drive
 *   the frontend's agentic behavior — the AI can trigger map views, route displays,
 *   eco-vision results, and incident dispatches through natural language.
 * - Provides graceful error handling with user-friendly fallback messages.
 */
import { useState, useCallback, useEffect } from 'react';
import { sendChatMessage } from '@/api';

export type UiAction = 'NONE' | 'SHOW_MAP' | 'SHOW_ROUTE' | 'REQUEST_IMAGE' | 'SHOW_ECO_RESULT' | 'DISPATCH_INCIDENT' | 'SHOW_CROWD' | 'HIDE_MAP' | 'CLEAR_MAP';

export interface ChatMessage {
  id: string;
  role: 'system' | 'user' | 'assistant';
  content: string;
  uiAction?: UiAction;
  payload?: Record<string, unknown>;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = sessionStorage.getItem('stadium_chat_history');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        return Array.isArray(parsed) ? parsed : [];
      } catch (e) {
        console.error('Failed to parse chat history', e);
      }
    }
    return [];
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    sessionStorage.setItem('stadium_chat_history', JSON.stringify(messages));
  }, [messages]);

  const sendMessage = useCallback(async (content: string, imageBase64?: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Map existing messages to API format
      const history = messages.map(m => ({
        role: m.role,
        content: m.content
      }));

      const response = await sendChatMessage(content, history, imageBase64);

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        uiAction: response.ui_action as UiAction,
        payload: response.payload,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      return assistantMessage;
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I am having trouble connecting to the stadium servers right now. Please try again.',
        uiAction: 'NONE',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [messages]);

  const addMessage = useCallback((msg: Omit<ChatMessage, 'id'>) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      ...msg,
    };
    setMessages((prev) => [...prev, newMessage]);
  }, []);

  return {
    messages,
    sendMessage,
    addMessage,
    isLoading,
  };
}
