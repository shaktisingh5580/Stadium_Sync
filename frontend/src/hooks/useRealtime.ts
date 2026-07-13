import { useState, useEffect, useCallback, useRef } from 'react';

interface EgressData {
  type: 'egress_route';
  target_gate_id: string;
  target_gate_name: string;
  distance_meters: number;
  path: Array<{x: number, y: number}>;
  message: string;
}

interface RealtimeState {
  isConnected: boolean;
  egressData: EgressData | null;
}

export function useRealtime() {
  const [state, setState] = useState<RealtimeState>({
    isConnected: false,
    egressData: null,
  });
  
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const token = localStorage.getItem('stadium_sync_token');
    if (!token) return;

    // Use localhost:8000 since we're in dev, or relative wss in prod
    const wsUrl = `ws://localhost:8000/api/v1/realtime/ws?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Real-time WebSocket connected');
      setState(prev => ({ ...prev, isConnected: true }));
      
      // Keep-alive ping
      setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Real-time event:', data);
        
        if (data.type === 'egress_route') {
          setState(prev => ({
            ...prev,
            egressData: data
          }));
        }
        
      } catch (e) {
        console.error('Failed to parse WS message', e);
      }
    };

    ws.onclose = () => {
      console.log('Real-time WebSocket disconnected');
      setState(prev => ({ ...prev, isConnected: false }));
      
      // Reconnect after 5 seconds
      setTimeout(() => connect(), 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      ws.close();
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const clearEgressAlert = useCallback(() => {
    setState(prev => ({ ...prev, egressData: null }));
  }, []);

  return {
    ...state,
    clearEgressAlert
  };
}
