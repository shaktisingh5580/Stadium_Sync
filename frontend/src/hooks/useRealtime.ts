/**
 * ===============================================================================
 * File: frontend/src/hooks/useRealtime.ts
 * Purpose: WebSocket connection hook - manages persistent bidirectional 
 *          connection, subscribes to real-time events (evacuation, crowd, 
 *          incidents), auto-reconnects on failure.
 * Architecture: useRealtime() hook manages WebSocket lifecycle. Emits events 
 *               via callback; auto-reconnect with exponential backoff on 
 *               connection failure.
 * Inputs: JWT token, event callback function.
 * Outputs: WebSocket connection state, event handler.
 * Hackathon Vertical: Real-Time Decision Support & Crowd Management
 * ===============================================================================
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface EgressData {
  type: 'egress_route';
  target_gate_id: string;
  target_gate_name: string;
  distance_meters: number;
  path: Array<{x: number, y: number}>;
  message: string;
}

interface EmergencyData {
  type: 'emergency_evacuate';
  hazard_zone?: string;
  message: string;
}

interface FlashData {
  type: 'flash_sale';
  vendor_name: string;
  section_id: string;
  discount: string;
  message: string;
  duration_mins: number;
}

interface ChatData {
  type: 'chat_message';
  role: 'system' | 'user' | 'assistant';
  content: string;
  target_ui?: 'NONE' | 'SHOW_MAP' | 'SHOW_ROUTE';
  target_location?: string;
}

interface RealtimeState {
  isConnected: boolean;
  egressData: EgressData | null;
  emergencyData: EmergencyData | null;
  flashData: FlashData | null;
  chatData: ChatData | null;
}

export function useRealtime() {
  const [state, setState] = useState<RealtimeState>({
    isConnected: false,
    egressData: null,
    emergencyData: null,
    flashData: null,
    chatData: null,
  });
  
  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatRef = useRef<number | null>(null);
  const reconnectRef = useRef<number | null>(null);

  const clearTimers = useCallback(() => {
    if (heartbeatRef.current !== null) {
      window.clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }
    if (reconnectRef.current !== null) {
      window.clearTimeout(reconnectRef.current);
      reconnectRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    const token = sessionStorage.getItem('stadium_sync_token');
    if (!token) return;

    if (reconnectRef.current !== null) {
      window.clearTimeout(reconnectRef.current);
      reconnectRef.current = null;
    }

    // Derive WebSocket URL from API base URL
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    const wsBase = baseUrl.replace(/^http/, 'ws');
    const wsUrl = `${wsBase}/ws?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setState(prev => ({ ...prev, isConnected: true }));
      
      // Keep one keep-alive interval per open socket and clear it on close.
      if (heartbeatRef.current !== null) window.clearInterval(heartbeatRef.current);
      heartbeatRef.current = window.setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'egress_route') {
          setState(prev => ({
            ...prev,
            egressData: data
          }));
        } else if (data.type === 'emergency_evacuate') {
          setState(prev => ({
            ...prev,
            emergencyData: data
          }));
        } else if (data.type === 'flash_sale') {
          setState(prev => ({
            ...prev,
            flashData: data
          }));
        } else if (data.type === 'chat_message') {
          setState(prev => ({
            ...prev,
            chatData: data
          }));
        }
        
      } catch {
        // Ignore malformed messages; the socket remains available for the next update.
      }
    };

    ws.onclose = () => {
      if (heartbeatRef.current !== null) {
        window.clearInterval(heartbeatRef.current);
        heartbeatRef.current = null;
      }
      setState(prev => ({ ...prev, isConnected: false }));

      // Reconnect only if this remains the active socket (not after unmount).
      if (wsRef.current === ws) {
        wsRef.current = null;
        reconnectRef.current = window.setTimeout(connect, 5000);
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimers();
      const socket = wsRef.current;
      wsRef.current = null;
      socket?.close();
    };
  }, [clearTimers, connect]);

  const clearEgressAlert = useCallback(() => {
    setState(prev => ({ ...prev, egressData: null }));
  }, []);

  const clearFlashAlert = useCallback(() => {
    setState(prev => ({ ...prev, flashData: null }));
  }, []);

  const clearChatAlert = useCallback(() => {
    setState(prev => ({ ...prev, chatData: null }));
  }, []);

  const clearEmergencyAlert = useCallback(() => {
    setState(prev => ({ ...prev, emergencyData: null }));
  }, []);

  return {
    ...state,
    clearEgressAlert,
    clearFlashAlert,
    clearChatAlert,
    clearEmergencyAlert
  };
}
