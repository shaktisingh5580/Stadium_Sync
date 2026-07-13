import { useState, useEffect } from 'react';
import { StadiumChat } from '@/components/StadiumChat';
import { QRScanner } from '@/components/auth/QRScanner';
import { cn } from '@/lib/utils';
import { AnimatePresence, motion } from 'framer-motion';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // Check if already authenticated on mount
  useEffect(() => {
    const token = localStorage.getItem('stadium_sync_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const handleScanSuccess = () => {
    setIsAuthenticated(true);
  };

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      <AnimatePresence mode="wait">
        {!isAuthenticated ? (
          <motion.div 
            key="scanner"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.5 }}
            className="w-full h-full"
          >
            <QRScanner onScanSuccess={handleScanSuccess} />
          </motion.div>
        ) : (
          <motion.div 
            key="chat"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className={cn(
              "transition-all duration-500 ease-in-out flex flex-col w-full h-full",
              "items-center justify-center bg-slate-950"
            )}
          >
            <StadiumChat />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
