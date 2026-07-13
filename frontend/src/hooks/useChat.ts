import { useState, useCallback } from 'react';
import { sendChatMessage } from '@/api';

export type UiAction = 'NONE' | 'SHOW_MAP' | 'SHOW_ROUTE' | 'REQUEST_IMAGE' | 'SHOW_ECO_RESULT' | 'DISPATCH_INCIDENT' | 'SHOW_CROWD' | 'HIDE_MAP';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  uiAction?: UiAction;
  payload?: any;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

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

  return {
    messages,
    sendMessage,
    isLoading,
  };
}
