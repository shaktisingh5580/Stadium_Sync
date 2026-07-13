import React, { useState } from 'react';
import { AlertTriangle, Send, Loader2 } from 'lucide-react';
import { GlowButton } from '../shared/GlowButton';
import { reportIncident } from '../../api';

export const IncidentPanel: React.FC = () => {
  const [category, setCategory] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const categories = [
    { id: 'spill', label: 'Spill / Clean up' },
    { id: 'broken_seat', label: 'Broken Seat' },
    { id: 'medical', label: 'Medical Assistance' },
    { id: 'security', label: 'Security Issue' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (description.length < 5 || !category) return;
    
    setIsSubmitting(true);
    setError(null);
    try {
      await reportIncident(`[${category}] ${description}`);
      setSubmitted(true);
      setTimeout(() => {
        setSubmitted(false);
        setCategory('');
        setDescription('');
      }, 3000);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to report incident.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-300">
      <div>
        <h3 className="text-lg font-medium text-slate-100 mb-1 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          Report Incident
        </h3>
        <p className="text-sm text-slate-400">See something wrong? Let us know and we'll dispatch a volunteer immediately.</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Category
          </label>
          <select 
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded-lg p-3 outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition-all appearance-none"
            required
          >
            <option value="" disabled>Select an issue...</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Description
          </label>
          <textarea 
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe what happened and where..."
            className="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded-lg p-3 outline-none focus:border-green-400 focus:ring-1 focus:ring-green-400 transition-all min-h-[100px] resize-none"
            minLength={5}
            required
          />
        </div>

        <GlowButton 
          type="submit" 
          disabled={!category || description.length < 5 || isSubmitting}
          className="w-full py-3 mt-2"
        >
          {isSubmitting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <Send className="w-4 h-4" />
              Dispatch Volunteer
            </>
          )}
        </GlowButton>
      </form>

      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <p className="text-xs text-red-400 font-medium">{error}</p>
        </div>
      )}

      {submitted && (
        <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-center animate-in fade-in zoom-in duration-300">
          <p className="text-sm text-green-400 font-medium">Incident Reported Successfully!</p>
          <p className="text-xs text-slate-300 mt-1">A volunteer is on their way to Section S204.</p>
        </div>
      )}
    </div>
  );
};
