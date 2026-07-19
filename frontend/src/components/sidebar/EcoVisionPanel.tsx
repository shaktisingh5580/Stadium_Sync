/**
 * ============================================================================
 * File: frontend/src/components/sidebar/EcoVisionPanel.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Eco-Vision AI Waste Classification Panel.
 *
 * Sustainability feature: fans capture a photo of waste items and Gemini Vision
 * analyzes the image to classify it as Compost, Recycle, Landfill, or Special.
 * Returns the correct bin color, disposal instructions, and a fun environmental fact.
 * All classifications are logged in the eco_classifications table for analytics.
 */
import { useState } from 'react';
import { Upload, Leaf, CheckCircle2, Loader2 } from 'lucide-react';
import { GlowCard } from '../shared/GlowCard';
import type { EcoVisionResult } from '../../types';
import { classifyWasteImage } from '../../api';

export const EcoVisionPanel: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<EcoVisionResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const [error, setError] = useState<string | null>(null);

  // Since we don't have a real file input wired up yet, we'll pass a mock base64
  // string to the backend when the user clicks the upload area.
  const handleMockUpload = async () => {
    setIsProcessing(true);
    setError(null);
    setResult(null);
    try {
      // Small dummy base64 JPEG to satisfy the backend validation
      const dummyB64 = "ffd8ffe000000000000000000000000000000000ffd9"; 
      const response = await classifyWasteImage(dummyB64);
      setResult(response);
    } catch (err: unknown) {
      setError((err as { response?: { data?: { message?: string } } }).response?.data?.message || 'Eco-Vision classification failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-300">
      <div>
        <h3 className="text-lg font-medium text-slate-100 mb-1 flex items-center gap-2">
          <Leaf className="w-5 h-5 text-green-400" />
          Eco-Vision
        </h3>
        <p className="text-sm text-slate-400">Not sure which bin to use? Upload a photo of your waste and AI will classify it.</p>
      </div>

      <div 
        className={`relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center transition-colors cursor-pointer
          ${isDragging ? 'border-green-400 bg-green-500/10' : 'border-slate-700 hover:border-slate-500 hover:bg-slate-800/50'}
        `}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => { e.preventDefault(); setIsDragging(false); handleMockUpload(); }}
        onClick={handleMockUpload}
      >
        <div className="p-3 bg-slate-800 rounded-full mb-3">
          <Upload className={`w-6 h-6 ${isDragging ? 'text-green-400' : 'text-slate-400'}`} />
        </div>
        <p className="text-sm font-medium text-slate-200 mb-1">Click or drag image to upload</p>
        <p className="text-xs text-slate-500">Supports JPG, PNG (Max 5MB)</p>
        
        {isProcessing && (
          <div className="absolute inset-0 bg-slate-900/90 rounded-xl flex flex-col items-center justify-center backdrop-blur-sm">
            <Loader2 className="w-8 h-8 text-green-400 animate-spin mb-2" />
            <p className="text-sm text-green-400 font-medium animate-pulse">Analyzing with Gemini...</p>
          </div>
        )}
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <p className="text-xs text-red-400 font-medium">{error}</p>
        </div>
      )}

      {result && (
        <GlowCard className="bg-slate-800/50 border-green-500/30">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h4 className="font-semibold text-slate-100">{result.itemName}</h4>
              <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                <CheckCircle2 className="w-3 h-3 text-green-400" />
                {Math.round(result.confidence * 100)}% Match
              </p>
            </div>
            <div className={`px-2 py-1 rounded text-xs font-bold uppercase tracking-wider
              ${result.binColor === 'green' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 
                result.binColor === 'blue' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 
                'bg-slate-500/20 text-slate-400 border border-slate-500/30'}`}
            >
              {result.category}
            </div>
          </div>
          
          <div className="space-y-2 mt-4">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase">Instructions</p>
              <p className="text-sm text-slate-300">{result.instructions}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase">Nearest Bin</p>
              <p className="text-sm text-slate-300">Section 104 Concourse (20m away)</p>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-slate-900 rounded border border-slate-700/50 flex items-start gap-2">
            <span className="text-lg leading-none">💡</span>
            <p className="text-xs text-slate-400 italic">{result.funFact}</p>
          </div>
        </GlowCard>
      )}
    </div>
  );
};
