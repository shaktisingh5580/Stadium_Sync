/**
 * ============================================================================
 * File: frontend/src/components/StadiumChat.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — StadiumChat (Primary Fan Interface).
 *
 * The central hub of the fan experience, combining:
 * - AI Chat: A Gemini-powered conversational concierge that handles navigation,
 *   accessibility queries, multilingual assistance, and eco-vision waste classification.
 * - Stadium Map: An interactive SVG-based map with real-time crowd density heatmap,
 *   seat highlighting, and animated egress route rendering.
 * - Sidebar Panels: Transit method selection, incident reporting, and eco-vision camera.
 * - Real-Time Alerts: WebSocket-driven egress notifications, emergency evacuations,
 *   flash sale promotions, and incident resolution updates.
 *
 * This component orchestrates state across useChat, useRealtime, and the API layer
 * to deliver a cohesive, responsive, and accessible fan experience.
 */
import React, { useState, useEffect } from 'react';
import { AnimatedAIChat } from './ui/animated-ai-chat';
import { useChat } from '@/hooks/useChat';
import { StadiumMap } from './map/StadiumMap';
import { AnimatePresence, motion } from 'framer-motion';
import { XIcon, MapIcon, BadgePercent } from 'lucide-react';

import { useRealtime } from '@/hooks/useRealtime';
import { EgressAlert } from './ui/EgressAlert';
import { triggerEgressSimulation } from '@/api';
import { fetchFanSession } from '@/api';
import type { FanSession } from '@/types';

/**
 * StadiumChat component is the main container for the Fan Persona interface.
 * It handles the chat interaction, realtime map routing, emergency egress alerts,
 * and flash sale notifications using WebSockets and the Gemini AI backend.
 * 
 * @returns {JSX.Element} The rendered StadiumChat layout.
 */
export const StadiumChat: React.FC = () => {
  const isDemoMode = import.meta.env.DEV || import.meta.env.VITE_DEMO_MODE === 'true';
  const { messages, sendMessage, addMessage, isLoading } = useChat();
  const { isConnected, egressData, emergencyData, flashData, chatData, clearEgressAlert, clearFlashAlert, clearChatAlert, clearEmergencyAlert } = useRealtime();
  const [mapVisible, setMapVisible] = useState(false);
  const [activeRoute, setActiveRoute] = useState<{ x: number, y: number }[] | undefined>();
  const [activeSeat, setActiveSeat] = useState<{ x: number, y: number } | undefined>();
  const [activePoi, setActivePoi] = useState<{x: number, y: number, name: string, type: string} | undefined>();
  const [activeHeatmap, setActiveHeatmap] = useState<Record<string, number> | undefined>();
  const [session, setSession] = useState<FanSession | null>(null);

  useEffect(() => {
    fetchFanSession().then(data => setSession(data)).catch(console.error);
  }, []);

  useEffect(() => {
    if (chatData) {
      const isSystem = chatData.role === 'system';
      addMessage({
        role: isSystem ? 'system' : 'assistant',
        content: isSystem ? `[STADIUM SYSTEM] ${chatData.content}` : chatData.content,
        uiAction: chatData.target_ui || 'NONE'
      });
      if (chatData.target_ui === 'SHOW_MAP' || chatData.target_ui === 'SHOW_ROUTE') {
        setMapVisible(true);
      }
      clearChatAlert();
    }
  }, [chatData, addMessage, clearChatAlert]);

  // Handle flash sales
  useEffect(() => {
    if (flashData) {
      // Determine coordinates based on vendor name, default to S203 Concessions location
      let x = 220, y = 540; 
      if (flashData.vendor_name?.includes('N1') || flashData.vendor_name?.includes('N2')) {
        x = 580; y = 260; // NE food
      }
      const poi = { x, y, name: flashData.vendor_name, type: 'food' };
      
      let route = undefined;
      let seat = undefined;
      if (session?.seat) {
        seat = { x: session.seat.svg_x, y: session.seat.svg_y };
        // Simple direct route from seat to concession stand
        route = [seat, poi];
      }

      addMessage({
        role: 'system',
        content: `[STADIUM SYSTEM] FLASH SALE: ${flashData.message}`,
        uiAction: 'SHOW_MAP',
        payload: { poi }
      });
      setMapVisible(true);
      setActivePoi(poi);
      setActiveRoute(route);
      setActiveSeat(seat);
      clearFlashAlert();
    }
  }, [flashData, addMessage, clearFlashAlert, session]);

  // Handle emergency egress automatically
  useEffect(() => {
    if (emergencyData) {
      if (egressData) {
        setMapVisible(true);
        setActiveRoute(egressData.path);
        setActiveSeat(egressData.path[0]);
        addMessage({
          role: 'system',
          content: `EMERGENCY EVACUATE, LEAVE THE STADIUM IMMEDIATELY. Your optimal route to ${egressData.target_gate_name} has been displayed on the map.`,
          uiAction: 'SHOW_ROUTE',
          payload: {
            route: { path: egressData.path }
          }
        });
        clearEgressAlert();
      } else {
        addMessage({
          role: 'system',
          content: `EMERGENCY EVACUATION. PLEASE PROCEED TO THE NEAREST SAFE EXIT IMMEDIATELY.`,
          uiAction: 'SHOW_MAP',
          payload: session?.seat ? {
            target: 'seat',
            seat_coordinates: { x: session.seat.svg_x, y: session.seat.svg_y }
          } : undefined
        });
      }
      clearEmergencyAlert();
    }
  }, [emergencyData, egressData, addMessage, clearEgressAlert, clearEmergencyAlert, session]);

  // Parse UI Actions from the latest message
  useEffect(() => {
    if (messages.length === 0) return;
    
    const latestMessage = messages[messages.length - 1];
    
    if ((latestMessage.role === 'assistant' || latestMessage.role === 'system') && latestMessage.uiAction) {
      switch (latestMessage.uiAction) {
        case 'SHOW_MAP':
          setMapVisible(true);
          setActiveRoute(undefined);
          if (latestMessage.payload?.poi) {
            setActivePoi((latestMessage.payload.poi as { x: number, y: number, name: string, type: string }));
            if ((latestMessage.payload.poi as { x: number, y: number, name: string, type: string }).type === 'seat') {
              setActiveSeat({ x: (latestMessage.payload.poi as { x: number, y: number, name: string, type: string }).x, y: (latestMessage.payload.poi as { x: number, y: number, name: string, type: string }).y });
            } else {
              setActiveSeat(undefined);
            }
          } else if (latestMessage.payload?.target === 'seat' && latestMessage.payload?.seat_coordinates) {
            setActiveSeat((latestMessage.payload.seat_coordinates as { x: number, y: number }));
            setActivePoi(undefined);
          } else {
            setActiveSeat(undefined);
            setActivePoi(undefined);
          }
          break;
        case 'SHOW_ROUTE':
          setMapVisible(true);
          if (latestMessage.payload?.route) {
            const routePath = (latestMessage.payload.route as { path: { x: number, y: number }[] }).path;
            setActiveRoute(routePath);
            if (routePath && routePath.length > 0) {
              setActiveSeat(routePath[0]);
            }
          }
          if (latestMessage.payload?.poi) {
            setActivePoi((latestMessage.payload.poi as { x: number, y: number, name: string, type: string }));
          } else {
            setActivePoi(undefined);
          }
          break;
        case 'SHOW_ECO_RESULT':
          if (latestMessage.payload?.route) {
            setMapVisible(true);
            const routePath = (latestMessage.payload.route as { path: { x: number, y: number }[] }).path;
            setActiveRoute(routePath);
            if (routePath && routePath.length > 0) {
              setActiveSeat(routePath[0]);
            }
          }
          break;
        case 'SHOW_CROWD':
          setMapVisible(true);
          setActiveRoute(undefined);
          setActiveSeat(undefined);
          setActivePoi(undefined);
          if (latestMessage.payload?.heatmapData) {
            setActiveHeatmap((latestMessage.payload.heatmapData as Record<string, number>));
          }
          break;
        case 'CLEAR_MAP':
          setActiveRoute(undefined);
          setActiveSeat(undefined);
          setActivePoi(undefined);
          setActiveHeatmap(undefined);
          break;
        case 'HIDE_MAP':
          setMapVisible(false);
          setActiveRoute(undefined);
          setActiveSeat(undefined);
          setActivePoi(undefined);
          setActiveHeatmap(undefined);
          break;
      }
    }
  }, [messages]);

  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleSendMessage = (content: string, imageBase64?: string) => {
    sendMessage(content, imageBase64);
  };

  return (
    <div className="relative w-full h-full overflow-hidden bg-slate-950 flex flex-col md:flex-row" role="region" aria-label="Stadium fan experience interface">
      
      {/* Main Chat Interface */}
      <div role="region" aria-label="AI concierge chat" className={`w-full h-full flex flex-col items-center justify-center p-4 transition-all duration-500 ${mapVisible && !isMobile ? 'md:w-1/2' : ''}`}>
        <div className="h-full w-full max-w-4xl flex flex-col items-center justify-center">
          <AnimatedAIChat 
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            fanSession={session}
          />
        </div>
      </div>

      {/* Full-screen Overlay Map Modal / Desktop Side Panel */}
      <AnimatePresence>
        {mapVisible && (
          <motion.div 
            initial={isMobile ? { opacity: 0, y: 50, scale: 0.95 } : { opacity: 0, x: '100%' }}
            animate={isMobile ? { opacity: 1, y: 0, scale: 1 } : { opacity: 1, x: 0 }}
            exit={isMobile ? { opacity: 0, y: 20, scale: 0.95 } : { opacity: 0, x: '100%' }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            className="absolute inset-0 md:left-auto md:w-1/2 z-50 bg-slate-950/80 backdrop-blur-xl flex flex-col md:border-l md:border-white/10"
          >
            {/* Floating Close Button */}
            <button 
              aria-label="Close Map"
              onClick={() => setMapVisible(false)}
              className="absolute top-4 right-4 z-[60] bg-slate-900/80 hover:bg-slate-800 text-white rounded-full p-3 transition-all flex items-center justify-center cursor-pointer shadow-lg border border-white/10"
              title="Close Map"
            >
              <XIcon size={20} />
            </button>

            {/* Map Container */}
            <div role="img" aria-label="Interactive stadium map showing sections, gates, and navigation routes" className="flex-1 w-full h-full flex items-center justify-center relative overflow-hidden">
              {/* Scaled Map - adjusted for full-screen overlay on different devices */}
              <div className="w-[800px] h-[800px] origin-center scale-[0.4] sm:scale-[0.5] md:scale-[0.65] lg:scale-[0.8] flex-shrink-0 relative">
                <StadiumMap 
                  egressRoute={activeRoute}
                  fanSeat={activeSeat}
                  targetPoi={activePoi}
                  needsAccessibility={session?.needsAccessibility}
                  heatmapData={activeHeatmap}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {egressData && !emergencyData && (
          <EgressAlert 
            message={egressData.message || "Please evacuate the stadium immediately."}
            gateName={egressData.target_gate_name}
            onAcknowledge={() => {
              setMapVisible(true);
              setActiveRoute(egressData.path);
              setActiveSeat(egressData.path[0]);
              clearEgressAlert();
            }}
          />
        )}
      </AnimatePresence>

      {/* Flash Sale Notification - Stays above everything */}
      <AnimatePresence>
        {flashData && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            className="absolute bottom-20 md:bottom-6 left-1/2 -translate-x-1/2 z-[80] w-[90%] max-w-sm bg-gradient-to-br from-emerald-500 to-teal-700 text-white p-5 rounded-2xl shadow-2xl border border-emerald-400/50"
            role="alert"
            aria-live="assertive"
          >
            <button 
              aria-label="Dismiss flash sale alert"
              onClick={clearFlashAlert}
              className="absolute top-3 right-3 p-1.5 bg-black/20 hover:bg-black/40 rounded-full transition-colors cursor-pointer"
            >
              <XIcon size={16} />
            </button>
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-white/20 rounded-full animate-bounce">
                <BadgePercent size={28} className="text-white" />
              </div>
              <div>
                <h3 className="font-bold text-xl leading-tight tracking-wide">FLASH SALE</h3>
                <p className="text-emerald-100 text-sm font-semibold">{flashData.discount}</p>
              </div>
            </div>
            <p className="text-sm mb-4 text-white/90 leading-relaxed">{flashData.message}</p>
            <button 
              aria-label="Route to flash sale"
              onClick={() => {
                clearFlashAlert();
                sendMessage(`Route me to ${flashData.vendor_name} for the flash sale!`);
              }}
              className="w-full py-2.5 bg-white text-emerald-700 hover:bg-emerald-50 rounded-xl font-bold text-sm transition-all shadow-lg active:scale-95 flex items-center justify-center gap-2 cursor-pointer"
            >
              <MapIcon size={16} />
              Route Me There
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Map Open Toggle Button - Shown only when map is hidden */}
      <AnimatePresence>
        {!mapVisible && (
          <motion.button
            aria-label="Open Map"
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            onClick={() => setMapVisible(true)}
            className="absolute top-4 right-4 md:top-6 md:right-6 z-40 px-3 md:px-4 py-2 md:py-3 bg-emerald-500/20 hover:bg-emerald-500/40 backdrop-blur-md border border-emerald-500/50 text-emerald-400 rounded-full flex items-center justify-center gap-2 cursor-pointer transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)]"
            title="Open Map"
          >
            <MapIcon size={20} />
            <span className="text-xs md:text-sm font-semibold">View Map</span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Development-only egress simulation. Production receives real signed events. */}
      {isDemoMode && <div className="absolute top-4 left-4 md:top-6 md:left-6 z-40 flex gap-2">
        <button
          aria-label="Simulate egress event"
          onClick={() => triggerEgressSimulation()}
          className="px-2 md:px-3 py-1 md:py-1.5 bg-red-500/20 hover:bg-red-500/40 border border-red-500/50 text-red-400 text-[10px] md:text-xs font-bold rounded-lg backdrop-blur-sm transition-colors cursor-pointer flex items-center gap-2"
        >
          <div className={`w-1.5 h-1.5 md:w-2 md:h-2 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-slate-500'}`} />
          <span className="hidden sm:inline">Simulate Egress</span>
          <span className="sm:hidden">Egress</span>
        </button>
      </div>}
    </div>
  );
};
