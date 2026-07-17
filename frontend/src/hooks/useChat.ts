import { useState, useCallback, useEffect } from 'react';
import { sendChatMessage } from '@/api';

export type UiAction = 'NONE' | 'SHOW_MAP' | 'SHOW_ROUTE' | 'REQUEST_IMAGE' | 'SHOW_ECO_RESULT' | 'DISPATCH_INCIDENT' | 'SHOW_CROWD' | 'HIDE_MAP' | 'CLEAR_MAP';

export interface ChatMessage {
  id: string;
  role: 'system' | 'user' | 'assistant';
  content: string;
  uiAction?: UiAction;
  payload?: any;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    const saved = localStorage.getItem('stadium_chat_history');
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
    localStorage.setItem('stadium_chat_history', JSON.stringify(messages));
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
