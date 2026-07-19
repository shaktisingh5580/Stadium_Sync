/**
 * ============================================================================
 * File: frontend/src/pages/AdminDashboard.tsx
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Organizer Command Center (AdminDashboard).
 *
 * Full-featured operations dashboard for venue staff and organizers:
 * - Digital Twin: Real-time stadium visualization with crowd density heatmap
 * - AI Copilot: Admin-facing Gemini chat with live operational context
 * - Incident Board: Live feed of AI-triaged incidents with volunteer assignments
 * - Emergency Controls: One-click evacuation broadcast to all connected fans
 * - Computer Vision: Simulated CV webhook for testing crowd/safety alerts
 * - Flash Sales: AI-driven vendor promotion targeting based on crowd flow
 *
 * Connects via WebSocket for real-time updates and polls /admin/state for data.
 * Protected by admin-role JWT authentication.
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ShieldAlert, Users, TrendingUp, Send, Loader2, RefreshCw, AlertTriangle, BadgePercent, Volume2, MapIcon, XIcon, InfoIcon, UserCircle2, UserCheck, Activity, CheckCircle2, Cctv } from 'lucide-react';
import { getAdminState, sendAdminChat, triggerEvacuation, evaluatePromotions, resolveIncident, triggerCVWebhook } from '@/api/admin';
import { triggerEgressSimulation } from '@/api';
import type { AdminState, Incident } from '@/api/admin';
import { StadiumMap } from '@/components/map/StadiumMap';

export function AdminDashboard() {
  const isDemoMode = import.meta.env.DEV || import.meta.env.VITE_DEMO_MODE === 'true';
  
  if (isDemoMode && !sessionStorage.getItem('stadium_sync_token')) {
    const demoAdminToken = import.meta.env.VITE_DEMO_ADMIN_TOKEN;
    if (demoAdminToken) {
      sessionStorage.setItem('stadium_sync_token', demoAdminToken);
    }
  }

  const [state, setState] = useState<AdminState | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Floating Overlay States
  const [mapOpen, setMapOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  // Chat State
  const [chatHistory, setChatHistory] = useState<{role: string, content: string, image?: string}[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  
  const [evacuating, setEvacuating] = useState(false);
  const [promoLoading, setPromoLoading] = useState(false);
  const [simLoading, setSimLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const fetchState = useCallback(async () => {
    try {
      const data = await getAdminState();
      setState(data);
    } catch (e) {
      console.error('Failed to fetch admin state:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchState();
    
    // Robust WebSocket Connection with auto-reconnect
    let ws: WebSocket | null = null;
    let reconnectTimeout: number;

    const connectWebSocket = () => {
      const token = sessionStorage.getItem('stadium_sync_token');
      if (!token) return;
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const wsBase = baseUrl.replace(/^http/, 'ws');
      ws = new WebSocket(`${wsBase}/ws?token=${encodeURIComponent(token)}`);
      
      ws.onopen = () => {
        console.log('Admin WebSocket connected successfully');
      };
      
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'admin_refresh_required') {
            console.log("WebSocket triggered refresh...");
            fetchState(); // Instantly refresh data when backend flags a change
          } else if (msg.type === 'chat_message' && msg.role === 'assistant') {
            setChatHistory(prev => [...prev, { role: 'assistant', content: msg.content }]);
          }
        } catch {
          // Ignore malformed WebSocket messages and keep the session alive.
        }
      };

      ws.onclose = () => {
        console.log('Admin WebSocket disconnected. Reconnecting in 3s...');
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (err) => {
        console.error("Admin WebSocket error:", err);
        ws?.close();
      };
    };

    connectWebSocket();

    return () => {
      clearTimeout(reconnectTimeout);
      if (ws) {
        ws.onclose = null; // Prevent reconnect on unmount
        ws.close();
      }
    };
  }, [fetchState]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [chatHistory]);

  const runSimulation = async () => {
    setSimLoading(true);
    try {
      // 1. Crowd Diversion (immediately)
      const crowdPromise = triggerCVWebhook({
        type: 'CROWD_CRITICAL',
        location: 'Court 3 Concessions',
        confidence: 0.95,
        description: 'Density exceeding 95% capacity. Acoustic anomaly detected (TENSE).'
      });

      // 2. Fire Alert (delayed)
      const firePromise = new Promise((resolve, reject) => {
        setTimeout(() => {
          triggerCVWebhook({
            type: 'FIRE_SMOKE',
            location: 'South Block',
            confidence: 0.98,
            description: 'Dense smoke and thermal anomaly detected in concourse.',
            image_url: 'https://images.unsplash.com/photo-1542282088-fe8426682b8f?auto=format&fit=crop&w=800&q=80'
          }).then(resolve).catch(reject);
        }, 3500);
      });

      await Promise.all([firePromise, crowdPromise]);
    } catch (e) {
      console.error("Failed to trigger CV webhook:", e);
    } finally {
      setSimLoading(false);
    }
  };

  // Proactive AI Simulation Sequence is manually triggered by the button

  const handleEvacuate = async () => {
    if (confirm("🚨 CRITICAL ACTION: Are you sure you want to trigger a stadium-wide evacuation?")) {
      setEvacuating(true);
      try {
        await triggerEvacuation("ALL_ZONES");
        await triggerEgressSimulation();
        alert("✅ Evacuation & Egress Simulation Triggered Successfully!");
        fetchState(); // Refresh the dashboard state to show any changes
      } catch (e) {
        alert("❌ Error triggering evacuation!");
        console.error(e);
      } finally {
        setEvacuating(false);
      }
    }
  };

  const handlePromos = async () => {
    setPromoLoading(true);
    try {
      const res = await evaluatePromotions();
      if (res.status === "promotions_triggered") {
        alert("Flash Sale Generated: " + res.promotion.message);
      }
    } catch {
      alert("Error generating promotions.");
    } finally {
      setPromoLoading(false);
    }
  };

  const handleResolveIncident = async (incidentId: string) => {
    try {
      await resolveIncident(incidentId);
      setSelectedIncident(null);
      // The backend will send an admin_refresh_required WS event which updates the dashboard!
    } catch (err) {
      console.error("Failed to resolve incident", err);
    }
  };

  const handleSend = async () => {
    if (!chatInput.trim()) return;
    const msg = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: msg }]);
    setChatLoading(true);

    try {
      const res = await sendAdminChat(msg, chatHistory);
      setChatHistory(prev => [...prev, { role: 'assistant', content: res.message }]);
    } catch {
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'Error communicating with AI Copilot.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return <div className="h-screen w-full flex items-center justify-center bg-[#0a0f1c] text-white"><Loader2 className="animate-spin w-8 h-8 text-blue-500" /></div>;
  }

  const allIncidents = state?.incidents || [];
  const criticalIncidents = allIncidents.filter(i => i.severity === 'critical' || i.severity === 'high');
  const predictiveAlerts = state?.crowd_map.sections.filter(s => s.predicted_mins_to_85 !== null && s.predicted_mins_to_85 < 20) || [];

  const heatmapData: Record<string, number> = {};
  if (state?.crowd_map?.sections) {
    state.crowd_map.sections.forEach(s => {
      heatmapData[s.section_id] = s.density_pct;
    });
  }

  return (
    <div className="flex fixed inset-0 bg-[#0a0f1c] text-slate-200 overflow-hidden font-sans selection:bg-blue-500/30">
      
      {/* Background ambient glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-900/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-indigo-900/20 blur-[120px] pointer-events-none" />

      {/* Main Dashboard */}
      <div className="flex-1 block p-8 overflow-y-auto w-full z-10 custom-scrollbar">
        <div className="flex justify-between items-center mb-10 max-w-7xl mx-auto w-full">
          <div>
            <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300 flex items-center gap-3">
              <ShieldAlert className="w-8 h-8 text-blue-500 drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
              STADIUM COMMAND CENTER
            </h1>
            <p className="text-slate-400 text-sm mt-1 font-medium tracking-wide">AI-Powered Operations & Real-Time Monitoring</p>
            <div className="mt-3 inline-flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg text-blue-300 text-xs font-semibold tracking-wide">
              <Activity className="w-4 h-4 text-blue-400 animate-pulse" />
              {isDemoMode ? 'SIMULATION MODE: generated events are clearly labelled and never mixed with production data.' : 'LIVE MODE: actions require an authenticated organizer and verified event source.'}
            </div>
          </div>
          
          <div className="flex gap-4">
            {isDemoMode && <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={runSimulation}
              disabled={simLoading}
              className="px-5 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-xl font-bold flex items-center gap-2 transition-all disabled:opacity-50"
            >
              {simLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  SIMULATING...
                </>
              ) : (
                <>
                  <Cctv className="w-5 h-5" />
                  TRIGGER CV SIMULATION
                </>
              )}
            </motion.button>}
            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handlePromos} 
              disabled={promoLoading}
              className="px-5 py-2.5 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-xl font-bold flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <BadgePercent className="w-5 h-5" />
              {promoLoading ? "ANALYZING..." : "RUN PROMO AI"}
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.05, boxShadow: "0px 0px 20px rgba(220, 38, 38, 0.4)" }}
              whileTap={{ scale: 0.95 }}
              onClick={handleEvacuate} 
              disabled={evacuating}
              className="px-5 py-2.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-xl font-bold flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <AlertTriangle className="w-5 h-5" />
              {evacuating ? "TRIGGERING..." : "EMERGENCY EVACUATE"}
            </motion.button>
            <motion.button 
              whileHover={{ scale: 1.1, rotate: 180 }}
              transition={{ duration: 0.3 }}
              onClick={fetchState} 
              className="p-3 bg-slate-800/50 border border-slate-700 hover:bg-slate-700/50 rounded-xl text-slate-300"
            >
              <RefreshCw className="w-5 h-5" />
            </motion.button>
          </div>
        </div>

        <div className="max-w-7xl mx-auto w-full">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-5 shadow-xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="text-slate-400 text-sm font-semibold mb-2 tracking-wide">STADIUM OCCUPANCY</div>
              <div className="text-4xl font-black text-white flex items-center gap-3">
                <Users className="w-8 h-8 text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.8)]" />
                {state?.crowd_map.total_occupancy_pct}%
              </div>
            </div>
            
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-5 shadow-xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="text-slate-400 text-sm font-semibold mb-2 tracking-wide">ACTIVE INCIDENTS</div>
              <div className="text-3xl lg:text-4xl font-black text-white flex items-center gap-3">
                <ShieldAlert className="w-7 h-7 text-blue-400 drop-shadow-[0_0_10px_rgba(96,165,250,0.8)]" />
                {allIncidents.length}
              </div>
            </div>

            <div className="bg-slate-900/40 backdrop-blur-xl border border-rose-900/30 rounded-2xl p-5 shadow-xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-rose-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="text-slate-400 text-sm font-semibold mb-2 tracking-wide">CRITICAL ISSUES</div>
              <div className="text-3xl lg:text-4xl font-black text-rose-400 flex items-center gap-3 drop-shadow-[0_0_15px_rgba(251,113,133,0.4)]">
                <AlertTriangle className="w-7 h-7 text-rose-500" />
                {criticalIncidents.length}
              </div>
            </div>

            <div className="bg-slate-900/40 backdrop-blur-xl border border-purple-900/30 rounded-2xl p-5 shadow-xl relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="text-slate-400 text-sm font-semibold mb-2 tracking-wide">ACOUSTIC PEAK</div>
              <div className="text-2xl lg:text-3xl font-black text-purple-300 flex items-center gap-3">
                <Volume2 className="w-6 h-6 text-purple-400 drop-shadow-[0_0_15px_rgba(192,132,252,0.6)]" />
                {state?.crowd_map.sections.some(s => s.acoustic_status === 'CHEERING' || s.acoustic_status === 'TENSE') ? 'LOUD' : 'NORMAL'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-8">
            {/* Predictive Alerts */}
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 flex flex-col min-h-[400px] shadow-xl">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-indigo-400 drop-shadow-[0_0_8px_rgba(129,140,248,0.8)]" />
                AI Predictive Congestion
              </h2>
              <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
                {predictiveAlerts.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-60">
                    <CheckCircle2 className="w-12 h-12 mb-3 text-emerald-500" />
                    <p className="font-medium tracking-wide text-sm">NO IMMINENT CONGESTION DETECTED</p>
                  </div>
                ) : (
                  predictiveAlerts.map(alert => (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      key={alert.section_id} 
                      className="bg-indigo-950/20 border border-indigo-500/20 rounded-xl p-4 hover:bg-indigo-900/30 transition-colors"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-bold text-indigo-300 text-lg">{alert.section_name}</span>
                        <div className="flex items-center gap-2">
                          {alert.acoustic_status && (
                            <span className="text-[10px] font-bold bg-purple-500/10 text-purple-300 px-2.5 py-1 rounded-md border border-purple-500/30 flex items-center gap-1 uppercase tracking-widest shadow-inner">
                              <Volume2 className="w-3 h-3" />
                              {alert.acoustic_status}
                            </span>
                          )}
                          <span className="text-xs font-bold bg-indigo-500/20 text-indigo-200 px-2.5 py-1 rounded-md shadow-inner border border-indigo-500/20">
                            {alert.density_pct.toFixed(1)}% VOL
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-indigo-200/80 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-indigo-400" />
                        Predicted to hit critical (85%) capacity in <span className="font-bold text-white">{alert.predicted_mins_to_85} mins</span>.
                      </p>
                    </motion.div>
                  ))
                )}
              </div>
            </div>

            {/* Active Incidents */}
            <div className="bg-slate-900/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 flex flex-col min-h-[400px] shadow-xl">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Activity className="w-6 h-6 text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                Live Incident Feed
              </h2>
              <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar">
                {allIncidents.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-60">
                    <CheckCircle2 className="w-12 h-12 mb-3 text-emerald-500" />
                    <p className="font-medium tracking-wide text-sm">ALL CLEAR. NO ACTIVE INCIDENTS.</p>
                  </div>
                ) : (
                  allIncidents.map(inc => (
                    <motion.div 
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      key={inc.id} 
                      className={`border rounded-xl p-4 transition-all hover:-translate-y-1 ${
                        inc.severity === 'critical' ? 'bg-rose-950/20 border-rose-500/30 hover:bg-rose-900/30 hover:border-rose-500/50 hover:shadow-[0_0_15px_rgba(225,29,72,0.15)]' : 
                        inc.severity === 'high' ? 'bg-amber-950/20 border-amber-500/30 hover:bg-amber-900/30' : 
                        'bg-slate-800/40 border-slate-700 hover:bg-slate-700/60'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-bold text-white tracking-wide uppercase text-sm">{inc.category} Alert</span>
                        <span className={`text-[10px] font-black px-2.5 py-1 rounded-md shadow-inner tracking-widest ${
                          inc.severity === 'critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 
                          inc.severity === 'high' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 
                          'bg-slate-700/80 text-slate-300 border border-slate-600'
                        }`}>
                          {inc.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-300/90 leading-relaxed line-clamp-2 italic border-l-2 border-slate-600 pl-3 my-3">
                        "{inc.description}"
                      </p>
                      <button 
                        aria-label={`Review ${inc.category || 'incident'} details`}
                        onClick={() => setSelectedIncident(inc)}
                        className={`mt-4 w-full text-xs py-2 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${
                          inc.severity === 'critical' ? 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20' :
                          'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50'
                        }`}
                      >
                        <InfoIcon className="w-4 h-4" /> REVIEW & DISPATCH
                      </button>
                    </motion.div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Action Buttons */}
      <div className="fixed bottom-10 left-10 flex flex-col gap-5 z-50">
        <motion.button 
          aria-label="Toggle crowd heatmap"
          whileHover={{ scale: 1.1, boxShadow: "0px 0px 20px rgba(52, 211, 153, 0.4)" }}
          whileTap={{ scale: 0.9 }}
          onClick={() => setMapOpen(!mapOpen)} 
          className="w-16 h-16 bg-emerald-600 rounded-2xl flex items-center justify-center shadow-xl transition-all"
        >
          <MapIcon className="w-7 h-7 text-white"/>
        </motion.button>
      </div>

      {/* Permanent Side Chat */}
      <div className="w-[450px] h-full bg-slate-900/95 border-l border-slate-700 shadow-2xl flex flex-col z-20 backdrop-blur-2xl shrink-0">
        <div className="p-5 border-b border-slate-800 bg-slate-900/90 flex justify-between items-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-transparent" />
          <div className="relative z-10">
            <h2 className="text-xl font-bold text-white flex items-center gap-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <ShieldAlert className="w-5 h-5 text-blue-400" />
              </div>
              AI Copilot
            </h2>
            <p className="text-xs text-slate-400 mt-1">Nvidia Llama 3.1 & Gemini Operations</p>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar" ref={chatContainerRef}>
          {chatHistory.length === 0 && (
                <div className="text-center text-slate-500 text-sm mt-12">
                  <ShieldAlert className="w-10 h-10 mx-auto mb-4 opacity-40 text-blue-400" />
                  <p className="font-medium text-slate-400">Command Center Copilot Active.</p>
                  <p className="mt-2 text-xs opacity-60">"Are there any bottlenecks forming near Gate C?"</p>
                </div>
              )}
              {chatHistory.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-5 py-3.5 shadow-sm border ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white border-blue-500 rounded-tr-sm' 
                      : 'bg-slate-800 text-slate-200 border-slate-700 rounded-tl-sm'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    {msg.image && (
                      <img src={msg.image} className="mt-3 rounded-lg border border-slate-600 shadow-md w-full object-cover aspect-video" alt="AI CCTV Attachment" />
                    )}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] rounded-2xl px-5 py-3 bg-slate-800 border border-slate-700 rounded-tl-sm">
                    <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
        </div>

        <div className="p-4 border-t border-slate-800 bg-slate-900">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleSend(); }}
            className="flex relative"
          >
            <input
              type="text"
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
              placeholder="Query stadium data..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-5 pr-14 py-3.5 text-sm text-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 focus:outline-none transition-all placeholder:text-slate-600"
            />
            <button 
              aria-label="Send message to AI copilot"
              type="submit" 
              disabled={!chatInput.trim() || chatLoading}
              className="absolute right-2 top-2 bottom-2 w-10 flex items-center justify-center bg-blue-600 rounded-lg text-white disabled:opacity-50 hover:bg-blue-500 transition-colors shadow-md"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {/* Floating Map Overlay */}
      <AnimatePresence>
        {mapOpen && (
          <motion.div 
            initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
            animate={{ opacity: 1, backdropFilter: "blur(12px)" }}
            exit={{ opacity: 0, backdropFilter: "blur(0px)" }}
            className="fixed inset-0 bg-slate-950/80 z-40 flex items-center justify-center p-8"
          >
            <motion.div 
              initial={{ scale: 0.95, y: 15 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 15 }}
              className="relative w-full h-full flex flex-col items-center justify-center max-w-7xl mx-auto"
            >
              <div className="absolute top-8 left-8 flex items-center gap-4 z-10 bg-slate-900/90 p-5 rounded-2xl backdrop-blur-xl border border-slate-700 shadow-2xl">
                <div className="p-3 bg-emerald-500/20 rounded-xl">
                  <MapIcon className="w-8 h-8 text-emerald-400" />
                </div>
                <div>
                  <h2 className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200 leading-tight">Live Crowd Heatmap</h2>
                  <p className="text-sm text-slate-400 font-medium">Real-time volumetric mapping</p>
                </div>
              </div>
              
              <button 
                aria-label="Close heatmap"
                onClick={() => setMapOpen(false)} 
                className="absolute top-8 right-8 z-10 p-4 bg-slate-900/90 hover:bg-slate-800 text-slate-300 rounded-full backdrop-blur-xl transition-all border border-slate-700 shadow-2xl hover:scale-110"
              >
                <XIcon className="w-6 h-6" />
              </button>

              <div className="w-full h-full flex items-center justify-center scale-95 origin-center">
                <StadiumMap heatmapData={heatmapData} />
              </div>
              
              {/* Heatmap Legend */}
              <div className="absolute bottom-10 right-10 bg-slate-900/90 backdrop-blur-xl border border-slate-700 p-5 rounded-2xl flex items-center gap-6 shadow-2xl">
                <span className="text-sm text-slate-400 font-bold uppercase tracking-wider">Density:</span>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-md bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                  <span className="text-sm font-semibold text-slate-200">{'< 60%'}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-md bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]"></div>
                  <span className="text-sm font-semibold text-slate-200">60-84%</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-md bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.5)]"></div>
                  <span className="text-sm font-semibold text-slate-200">{'>= 85%'}</span>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Incident Details Modal */}
      <AnimatePresence>
        {selectedIncident && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4"
          >
            <motion.div
              initial={{ scale: 0.95, y: 15 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 15 }}
              className="bg-slate-900 border border-slate-700 rounded-3xl p-8 max-w-lg w-full shadow-[0_20px_60px_rgba(0,0,0,0.6)] relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-b from-slate-800/50 to-transparent pointer-events-none" />
              
              <button 
                aria-label="Close incident details modal"
                onClick={() => setSelectedIncident(null)}
                className="absolute top-6 right-6 text-slate-400 hover:text-white transition-colors p-2 bg-slate-800/80 rounded-full hover:bg-slate-700 z-10"
              >
                <XIcon className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-4 mb-8 relative z-10">
                <div className={`p-3 rounded-2xl shadow-inner ${selectedIncident.severity === 'critical' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : selectedIncident.severity === 'high' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-slate-800 text-slate-300 border border-slate-700'}`}>
                  <AlertTriangle className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-white capitalize tracking-wide">{selectedIncident.category || 'General'} Incident</h3>
                  <p className="text-sm text-slate-400 flex items-center gap-2 mt-1">
                    Status: <span className="text-emerald-400 uppercase text-xs font-black px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded shadow-sm">{selectedIncident.status}</span>
                  </p>
                </div>
              </div>

              <div className="space-y-6 relative z-10">
                <div>
                  <h4 className="text-xs uppercase text-slate-500 font-bold mb-2 tracking-widest pl-1">Reporter Log</h4>
                  <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800 flex items-start gap-4">
                    {selectedIncident.ticket_id?.startsWith('sim-') ? <Cctv className="w-10 h-10 text-slate-500 mt-1" /> : <UserCircle2 className="w-10 h-10 text-slate-500 mt-1" />}
                    <div>
                      <p className="text-sm text-white font-bold">
                        {selectedIncident.ticket_id?.startsWith('sim-') ? 'Computer Vision Node (Auto-Detect)' : 'Carlos Rivera (Fan App)'}
                      </p>
                      <p className="text-xs text-slate-400 mt-1 font-medium bg-slate-800 inline-block px-2 py-0.5 rounded">
                        {selectedIncident.ticket_id?.startsWith('sim-') ? selectedIncident.location_description : 'Section N101, Row 1, Seat 1'}
                      </p>
                      <div className="mt-3 p-3 bg-blue-900/10 border-l-4 border-blue-500/50 rounded-r-lg">
                        <p className="text-sm text-slate-300 italic">
                          "{selectedIncident.description}"
                        </p>
                        {selectedIncident.image_url && (
                          <div className="mt-3 rounded-lg overflow-hidden border border-slate-800">
                            <img src={selectedIncident.image_url} alt="Incident visualization" className="w-full h-auto object-cover max-h-48" />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xs uppercase text-slate-500 font-bold mb-2 tracking-widest pl-1">Dispatch Protocol</h4>
                  <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800 flex items-start gap-4">
                    <UserCheck className="w-10 h-10 text-blue-500 mt-1" />
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <p className="text-sm text-white font-bold">{selectedIncident.volunteer_name || "Response Team Alpha"}</p>
                        <span className="text-[10px] bg-blue-500/20 text-blue-400 border border-blue-500/30 px-2.5 py-0.5 rounded-full uppercase font-bold tracking-widest">{selectedIncident.volunteer_name ? "Assigned" : "Pending"}</span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1.5 font-medium">{selectedIncident.volunteer_name ? "Currently assessing situation on-site." : "Awaiting unit assignment..."}</p>
                    </div>
                  </div>
                </div>

                <div className="border-t border-slate-800 pt-6 mt-8">
                  <div className="bg-gradient-to-r from-emerald-900/30 to-slate-900 border border-emerald-500/30 rounded-2xl p-5 shadow-lg">
                    <h4 className="text-xs uppercase text-emerald-400 font-bold mb-3 flex items-center gap-2 tracking-widest">
                      <Activity className="w-4 h-4" />
                      AI Copilot Assessment
                    </h4>
                    <p className="text-sm text-emerald-100/80 leading-relaxed font-medium">
                      <span className="text-emerald-400 font-bold">Automated Routing:</span> The AI has assigned the closest unit to this section. Medical staff pre-notified.
                    </p>
                    <div className="mt-5 flex gap-3">
                      <button 
                        aria-label="Close incident details"
                        onClick={() => setSelectedIncident(null)}
                        className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 py-3 rounded-xl text-sm font-bold transition-all border border-slate-700 hover:scale-[1.02]"
                      >
                        CLOSE
                      </button>
                      <button 
                        aria-label="Mark incident as resolved"
                        onClick={() => handleResolveIncident(selectedIncident.id)}
                        className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(16,185,129,0.4)]"
                      >
                        <CheckCircle2 className="w-5 h-5" />
                        MARK RESOLVED (NOTIFY ZONE)
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
