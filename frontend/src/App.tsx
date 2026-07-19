/**
 * ===============================================================================
 * File: frontend/src/App.tsx
 * Purpose: Root React component - orchestrates route logic, authentication 
 *          state, WebSocket initialization, theme provider setup.
 * Architecture: Central component tree orchestrator. Manages JWT token 
 *               (sessionStorage), initializes WebSocket, conditional rendering 
 *               based on auth role (fan vs admin).
 * Inputs: JWT token from sessionStorage, route/page context.
 * Outputs: Rendered UI (FanInterface or AdminDashboard) based on auth state.
 * Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
 * ===============================================================================
 */

import { lazy, Suspense, useState, useEffect } from 'react';
import { QRScanner } from '@/components/auth/QRScanner';
import { fetchDemoCredentials } from '@/api';
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

  // Check if already authenticated on mount
  useEffect(() => {
    const token = sessionStorage.getItem('stadium_sync_token');
    if (token) {
      setIsAuthenticated(true);
      if (getRoleFromToken(token) === 'admin') {
        setIsAdmin(true);
      }
    } else if (window.location.pathname === '/admin') {
      // Auto-bypass for /admin URL
      const doAdminBypass = async () => {
        try {
          let adminToken = import.meta.env.VITE_DEMO_ADMIN_TOKEN;
          try {
            const creds = await fetchDemoCredentials();
            adminToken = creds.admin_token;
          } catch (e) {
            console.warn("Could not fetch demo credentials from backend, falling back to local env vars.");
          }
          if (adminToken) {
            sessionStorage.setItem('stadium_sync_token', adminToken);
            setIsAuthenticated(true);
            setIsAdmin(true);
            // Optionally clear the URL back to root without refreshing
            window.history.replaceState({}, '', '/');
          }
        } catch (e) {
          console.error("Failed auto admin bypass", e);
        }
      };
      void doAdminBypass();
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
