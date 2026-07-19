/**
 * ============================================================================
 * File: frontend/src/components/layout/StatusBar.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Connection Status Bar Component.
 *
 * Shows real-time connection indicators: WebSocket status, current time,
 * and security badge. Provides visual feedback to fans about their
 * connection to the stadium's real-time data feeds.
 */
import React from 'react';
import { Wifi, Clock, ShieldCheck } from 'lucide-react';

export const StatusBar: React.FC = () => {
  const [time, setTime] = React.useState(new Date().toLocaleTimeString());

  React.useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <footer className="h-10 flex items-center justify-between px-4 bg-slate-900 border-t border-slate-800 shrink-0 text-xs text-slate-400">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-green-400">
          <Wifi className="w-3.5 h-3.5" />
          <span>System Online</span>
        </div>
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Secure Connection</span>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <Clock className="w-3.5 h-3.5" />
        <span className="font-mono">{time}</span>
      </div>
    </footer>
  );
};
