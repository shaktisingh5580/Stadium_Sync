import React, { useState } from 'react';
import { Scanner } from '@yudiel/react-qr-scanner';
import { motion } from 'framer-motion';
import { ScanLine, ShieldCheck, Ticket, UserCircle, QrCode } from 'lucide-react';
import { loginWithQR } from '@/api';

interface QRScannerProps {
  onScanSuccess: () => void;
}

export function QRScanner({ onScanSuccess }: QRScannerProps) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async (text: string) => {
    if (loading) return;
    try {
      setLoading(true);
      setError(null);
      console.log('Scanned payload:', text);
      await loginWithQR(text);
      onScanSuccess();
    } catch (err: any) {
      console.error('Scan Error:', err);
      setError('Invalid Ticket QR Code. Please try again.');
      setLoading(false);
    }
  };

  const handleBypass = async () => {
    // For Hackathon Demo Purposes
    const mockPayload = JSON.stringify({
      ticket_id: "ticket-001", 
      match_id: "M2026-QF1", 
      checksum: "642f90c0d004"
    });
    await handleScan(mockPayload);
  };

  return (
    <div className="relative flex flex-col items-center justify-center w-full h-full min-h-screen bg-slate-950 text-slate-100 overflow-hidden">
      
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
        <div className="relative w-full aspect-square max-w-[320px] rounded-2xl overflow-hidden border border-slate-700/50 shadow-2xl shadow-emerald-900/20 bg-slate-900">
          
          {loading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-sm z-20">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              >
                <ScanLine className="w-12 h-12 text-emerald-500 mb-4" />
              </motion.div>
              <span className="text-emerald-400 font-medium animate-pulse">Authenticating Ticket...</span>
            </div>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <Scanner 
                onResult={(text, result) => handleScan(text)} 
                onError={(error) => console.log(error?.message)} 
                options={{ delayBetweenScanAttempts: 1000 }}
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
            className="mt-6 px-4 py-3 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm text-center w-full max-w-[320px]"
          >
            {error}
          </motion.div>
        )}

        <div className="mt-12 flex flex-col items-center gap-4 w-full">
          {/* Dev Bypass Button */}
          <button 
            onClick={handleBypass}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium transition-colors border border-slate-700 hover:border-slate-600 disabled:opacity-50"
          >
            <Ticket className="w-4 h-4" />
            <span>Dev Bypass: Auto-Login</span>
          </button>
        </div>
      </motion.div>
    </div>
  );
}
