import React, { useState } from 'react';
import { GlowCard } from '../shared/GlowCard';
import { GlowButton } from '../shared/GlowButton';
import { Train, Bus, Car, Navigation, Loader2 } from 'lucide-react';
import type { FanSession } from '../../types';
import { updateTransitMethod, fetchEgressRoute } from '../../api';

interface TransitPanelProps {
  session: FanSession;
  onUpdateTransit: (method: string) => void;
}

export const TransitPanel: React.FC<TransitPanelProps> = ({ session, onUpdateTransit }) => {
  const [selected, setSelected] = useState<string | null>(session.transitMethod);

  const [isLoading, setIsLoading] = useState(false);
  const [routeData, setRouteData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const transitOptions = [
    { id: 'metro', label: 'Metro', icon: Train },
    { id: 'bus', label: 'Bus', icon: Bus },
    { id: 'rideshare', label: 'Rideshare', icon: Car },
    { id: 'parking', label: 'Parking', icon: Car },
  ];

  const handleGenerate = async () => {
    if (!selected) return;
    setIsLoading(true);
    setError(null);
    try {
      await updateTransitMethod(selected);
      const route = await fetchEgressRoute();
      setRouteData(route);
      onUpdateTransit(selected);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to generate route.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-300">
      <div>
        <h3 className="text-lg font-medium text-slate-100 mb-1">Egress Navigation</h3>
        <p className="text-sm text-slate-400">Select how you're getting home to generate the optimal exit route from your seat.</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {transitOptions.map((option) => {
          const Icon = option.icon;
          const isActive = selected === option.id;
          return (
            <GlowCard 
              key={option.id}
              active={isActive}
              onClick={() => setSelected(option.id)}
              className="cursor-pointer flex flex-col items-center justify-center p-4 gap-2 transition-transform hover:scale-105"
            >
              <Icon className={`w-6 h-6 ${isActive ? 'text-green-400' : 'text-slate-400'}`} />
              <span className={`text-sm font-medium ${isActive ? 'text-green-400' : 'text-slate-300'}`}>
                {option.label}
              </span>
            </GlowCard>
          );
        })}
      </div>

      <GlowButton 
        onClick={handleGenerate} 
        disabled={!selected || isLoading}
        className="w-full py-3 mt-4"
      >
        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Navigation className="w-4 h-4" />}
        {isLoading ? 'Computing...' : 'Generate Exit Route'}
      </GlowButton>

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <p className="text-xs text-red-400 font-medium">{error}</p>
        </div>
      )}

      {routeData && (
        <div className="mt-4 p-4 rounded-lg bg-green-500/10 border border-green-500/20">
          <p className="text-sm text-green-400 mb-1 font-medium">Route Generated!</p>
          <div className="flex justify-between items-center text-xs text-slate-300">
            <span>Target Gate: <strong>{routeData.target_gate_name}</strong></span>
            <span>Walk: <strong>~{routeData.estimated_time_mins} mins</strong></span>
          </div>
        </div>
      )}
    </div>
  );
};
