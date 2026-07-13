import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, ArrowRightCircle } from 'lucide-react';

interface EgressAlertProps {
  message: string;
  gateName: string;
  onAcknowledge: () => void;
}

export function EgressAlert({ message, gateName, onAcknowledge }: EgressAlertProps) {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="absolute inset-0 z-50 flex items-center justify-center p-6 bg-slate-950/90 backdrop-blur-md"
    >
      <motion.div 
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        className="w-full max-w-lg bg-red-500/10 border border-red-500/30 rounded-3xl p-8 shadow-2xl shadow-red-900/50 flex flex-col items-center text-center overflow-hidden relative"
      >
        {/* Flashing background effect */}
        <motion.div 
          animate={{ opacity: [0.1, 0.3, 0.1] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="absolute inset-0 bg-red-500 pointer-events-none"
        />

        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ repeat: Infinity, duration: 1 }}
        >
          <AlertTriangle className="w-20 h-20 text-red-500 mb-6 relative z-10" />
        </motion.div>

        <h2 className="text-3xl font-black text-white uppercase tracking-wider mb-2 relative z-10">
          Egress Initiated
        </h2>
        
        <p className="text-red-200 text-lg mb-6 relative z-10">
          {message}
        </p>

        <div className="bg-slate-900/80 rounded-2xl p-6 w-full mb-8 relative z-10 border border-slate-700/50">
          <p className="text-slate-400 font-medium mb-1">Your Designated Exit</p>
          <p className="text-3xl font-bold text-emerald-400">{gateName}</p>
        </div>

        <button 
          onClick={onAcknowledge}
          className="relative z-10 flex items-center gap-2 px-8 py-4 bg-red-600 hover:bg-red-500 text-white rounded-xl font-bold text-lg transition-colors w-full justify-center group shadow-lg shadow-red-900"
        >
          <span>View Escape Route</span>
          <ArrowRightCircle className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
        </button>
      </motion.div>
    </motion.div>
  );
}
