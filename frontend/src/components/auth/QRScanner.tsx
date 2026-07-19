/**
 * ============================================================================
 * File: frontend/src/components/auth/QRScanner.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — QR Code Ticket Scanner Component.
 *
 * Entry point for fan authentication. Uses the device camera to scan the ticket's
 * QR code, which contains a signed JSON payload (ticket_id, match_id, checksum).
 * On successful scan, sends the payload to POST /auth/scan-ticket, stores the JWT,
 * and triggers the parent callback to transition into the StadiumChat interface.
 *
 * Includes a demo/manual entry mode for development and accessibility testing.
 * Supports JWT-based authentication with HMAC-verified QR ticket payloads.
 */
import { useState } from 'react';
import { Scanner } from '@yudiel/react-qr-scanner';
import { motion } from 'framer-motion';
import { ScanLine, ShieldCheck, Ticket } from 'lucide-react';
import { loginWithQR } from '@/api';

interface QRScannerProps {
  onScanSuccess: () => void;
}

export function QRScanner({ onScanSuccess }: QRScannerProps) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const isDemoMode = import.meta.env.DEV || import.meta.env.VITE_DEMO_MODE === 'true';

  const handleScan = async (text: string) => {
    if (loading) return;
    try {
      setLoading(true);
      setError(null);
      await loginWithQR(text);
      onScanSuccess();
    } catch {
      setError('Invalid Ticket QR Code. Please try again.');
      setLoading(false);
    }
  };

  const handleBypass = async () => {
    const mockPayload = import.meta.env.VITE_DEMO_QR_PAYLOAD;
    if (!mockPayload) {
      setError('Demo ticket is not configured. Please scan a valid ticket.');
      return;
    }
    await handleScan(mockPayload);
  };

  return (
    <div className="relative flex flex-col items-center justify-center w-full h-full min-h-screen bg-slate-950 text-slate-100 overflow-hidden" role="region" aria-label="Ticket authentication">
      
      {/* Background Decorative Elements */}
      <div className="absolute inset-0 bg-emerald-500/5 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 blur-[100px] rounded-full pointer-events-none" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="z-10 flex flex-col items-center w-full max-w-md p-6"
      >
        <div className="flex items-center gap-3 mb-8">
          <ShieldCheck className="w-10 h-10 text-emerald-400" />
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
            Stadium Sync
          </h1>
        </div>

        <p className="text-slate-400 text-center mb-8">
          Scan your digital ticket QR code to enter the interactive stadium experience.
        </p>

        {/* Scanner Container with futuristic border */}
        <div className="relative w-full aspect-square max-w-[320px] rounded-2xl overflow-hidden border border-slate-700/50 shadow-2xl shadow-emerald-900/20 bg-slate-900" role="region" aria-label="QR code scanner viewfinder">
          
          {loading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-sm z-20">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              >
                <ScanLine className="w-12 h-12 text-emerald-500 mb-4" />
              </motion.div>
              <span className="text-emerald-400 font-medium animate-pulse" role="status" aria-live="polite">Authenticating Ticket...</span>
            </div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <Scanner 
                onScan={(results) => {
                  const value = results[0]?.rawValue;
                  if (value) void handleScan(value);
                }}
                onError={() => setError('Camera access is unavailable. Please allow camera access and try again.')}
              />
              {/* Corner Accents */}
              <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-emerald-500 rounded-tl-lg z-10 pointer-events-none" />
              <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-emerald-500 rounded-tr-lg z-10 pointer-events-none" />
              <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-emerald-500 rounded-bl-lg z-10 pointer-events-none" />
              <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-emerald-500 rounded-br-lg z-10 pointer-events-none" />
            </div>
          )}
        </div>

        {error && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-6 px-4 py-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm text-center w-full max-w-[320px]" role="alert" aria-live="assertive"
          >
            {error}
          </motion.div>
        )}

        {isDemoMode && <div className="mt-12 flex flex-col items-center gap-4 w-full">
          {/* Development-only demo shortcut; excluded from normal production builds. */}
          <button 
            aria-label="Developer bypass login"
            onClick={handleBypass}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium transition-colors border border-slate-700 hover:border-slate-600 disabled:opacity-50"
          >
            <Ticket className="w-4 h-4" />
            <span>Dev Bypass: Auto-Login</span>
          </button>
        </div>}
      </motion.div>
    </div>
  );
}
