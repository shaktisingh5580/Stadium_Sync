import React from 'react';
import { Activity, Menu } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="h-16 flex items-center justify-between px-6 bg-slate-900/50 border-b border-slate-800 backdrop-blur-md shrink-0">
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
        </div>
      </div>
    </header>
  );
};
