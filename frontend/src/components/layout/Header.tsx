/**
 * ===============================================================================
 * File: frontend/src/components/layout/Header.tsx
 * Purpose: Navigation header - displays fan name, match info, token expiry 
 *          warning, logout button.
 * Architecture: Always-visible header at top. Shows current fan name, match 
 *               name/time, token countdown (e.g., "Expires in 5 min"), logout.
 * Inputs: User context (name), JWT expiry time, match info.
 * Outputs: Header UI with user state and logout action.
 * Hackathon Vertical: Navigation & Authentication
 * ===============================================================================
 */

import React from 'react';
import { Activity } from 'lucide-react';

/**
 * Header component displaying the application title and user information.
 * 
 * @returns {JSX.Element} The rendered header.
 */
export const Header: React.FC = () => {
  return (
    <header role="banner" className="h-16 flex items-center justify-between px-6 bg-slate-900/50 border-b border-slate-800 backdrop-blur-md shrink-0">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-green-500/10 rounded-lg border border-green-500/30">
          <Activity className="w-5 h-5 text-green-400" />
        </div>
        <h1 className="text-xl font-bold tracking-wider text-slate-100 uppercase">
          Stadium <span className="text-green-400">Sync</span>
        </h1>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="text-right">
          <p className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Match</p>
          <p className="text-sm text-slate-200">World Cup QF1 - M2026</p>
        </div>
        <div className="w-px h-8 bg-slate-700"></div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-sm font-bold border border-slate-600">
            DF
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-slate-200">Demo Fan</p>
            <p className="text-xs text-slate-400">Sec S204 • Row A • Seat 1</p>
          </div>
          <button 
            onClick={() => {
              sessionStorage.removeItem('stadium_sync_token');
              sessionStorage.removeItem('stadium_sync_auth_provider');
              window.location.reload();
            }}
            className="ml-4 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 rounded border border-slate-700 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
};
