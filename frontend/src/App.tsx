/**
 * ============================================================================
 * File: frontend/src/App.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Root Application Component.
 *
 * Orchestrates the top-level authentication flow:
 * 1. If no JWT token exists in sessionStorage, renders the QRScanner for ticket-based login.
 * 2. Once authenticated, transitions to the StadiumChat AI concierge interface.
 * 3. If `?admin=true` query param is present, renders the AdminDashboard (Organizer Command Center).
 *
 * Uses React.lazy + Suspense for code-splitting the Chat and Admin bundles,
 * and Framer Motion's AnimatePresence for smooth page transitions.
 */
import { lazy, Suspense, useState, useEffect } from 'react';
import { QRScanner } from '@/components/auth/QRScanner';
import { cn } from '@/lib/utils';
import { AnimatePresence, motion } from 'framer-motion';

const StadiumChat = lazy(() =>
  import('@/components/StadiumChat').then(({ StadiumChat }) => ({ default: StadiumChat }))
);
const AdminDashboard = lazy(() =>
  import('@/pages/AdminDashboard').then(({ AdminDashboard }) => ({ default: AdminDashboard }))
);

function LoadingScreen() {
  return <div className="flex h-screen items-center justify-center bg-slate-950 text-slate-200">Loading Stadium Sync…</div>;
}

function getRoleFromToken(token: string): string | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.role || (payload.admin ? 'admin' : 'user');
  } catch {
    return null;
  }
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  // Check if already authenticated on mount or if admin demo bypass is used
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('admin') === 'true') {
      setIsAuthenticated(true);
      setIsAdmin(true);
      return;
    }

    const token = sessionStorage.getItem('stadium_sync_token');
    if (token) {
      setIsAuthenticated(true);
      if (getRoleFromToken(token) === 'admin') {
        setIsAdmin(true);
      }
    }
  }, []);

  const handleScanSuccess = () => {
    setIsAuthenticated(true);
    const token = sessionStorage.getItem('stadium_sync_token');
    if (token && getRoleFromToken(token) === 'admin') {
      setIsAdmin(true);
    }
  };

  if (isAuthenticated && isAdmin) {
    return <Suspense fallback={<LoadingScreen />}><AdminDashboard /></Suspense>;
  }

  return (
    <div id="main-content" role="main" aria-label="Stadium Sync main content" className="flex h-screen w-full bg-background text-foreground overflow-hidden">
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
            <Suspense fallback={<LoadingScreen />}><StadiumChat /></Suspense>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
