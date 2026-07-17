import { useState, useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ShieldAlert, Users, TrendingUp, Send, Loader2, RefreshCw, AlertTriangle, BadgePercent, Volume2, MessageCircle, MapIcon, XIcon, InfoIcon, UserCircle2, UserCheck, Activity } from 'lucide-react';
import { getAdminState, sendAdminChat, triggerEvacuation, evaluatePromotions, resolveIncident } from '@/api/admin';
import { triggerEgressSimulation } from '@/api';
import type { AdminState } from '@/api/admin';
import { StadiumMap } from '@/components/map/StadiumMap';

export function AdminDashboard() {
  const [state, setState] = useState<AdminState | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Floating Overlay States
  const [chatOpen, setChatOpen] = useState(false);
  const [mapOpen, setMapOpen] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<any | null>(null);

  // Chat State
  const [chatHistory, setChatHistory] = useState<{role: string, content: string}[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  
  const [evacuating, setEvacuating] = useState(false);
  const [promoLoading, setPromoLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const handleEvacuate = async () => {
    if (confirm("Are you absolutely sure? This will trigger a stadium-wide evacuation alert to all fans.")) {
      setEvacuating(true);
      try {
        await triggerEvacuation("ALL_ZONES");
        await triggerEgressSimulation();
        alert("EVACUATION TRIGGERED SUCCESSFULLY.");
      } catch (e) {
        alert("Error triggering evacuation!");
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
      } else {
        alert(res.message || "No promotions generated.");
      }
    } catch (e) {
      alert("Error generating promotions.");
    } finally {
      setPromoLoading(false);
    }
  };

  const fetchState = async () => {
    try {
      const data = await getAdminState();
      setState(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchState();
    
    // Connect to WebSocket for instant real-time updates
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';
    const ws = new WebSocket(`${wsUrl}?token=admin-demo-token`);
    
    ws.onopen = () => console.log('Admin WebSocket connected');
    
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'admin_refresh_required') {
          fetchState();
        }
      } catch (e) {
        console.error('WebSocket message parsing error', e);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSend = async () => {
    if (!chatInput.trim()) return;
    const msg = chatInput.trim();
    setChatInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: msg }]);
    setChatLoading(true);

    try {
      const res = await sendAdminChat(msg, chatHistory);
      setChatHistory(prev => [...prev, { role: 'assistant', content: res.message }]);
    } catch (e) {
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'Error communicating with AI Copilot.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return <div className="h-screen w-full flex items-center justify-center bg-slate-950 text-white"><Loader2 className="animate-spin w-8 h-8" /></div>;
  }

  const criticalIncidents = state?.incidents.filter(i => i.severity === 'critical' || i.severity === 'high') || [];
  const allIncidents = state?.incidents || [];
  const predictiveAlerts = state?.crowd_map.sections.filter(s => s.predicted_mins_to_85 !== null && s.predicted_mins_to_85 < 20) || [];

  // Build heatmap data object mapping section_id to density_pct
  const heatmapData: Record<string, number> = {};
  if (state?.crowd_map?.sections) {
    state.crowd_map.sections.forEach(s => {
      heatmapData[s.section_id] = s.density_pct;
    });
  }

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-200 overflow-hidden font-sans relative">
      {/* Dashboard Full Width */}
      <div className="flex-1 flex flex-col p-6 overflow-y-auto w-full">
        <div className="flex justify-between items-center mb-8 max-w-7xl mx-auto w-full">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-6 h-6 text-blue-500" />
            Command Center
          </h1>
          <div className="flex gap-4">
            <button 
              onClick={handlePromos} 
              disabled={promoLoading}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              <BadgePercent className="w-5 h-5" />
              {promoLoading ? "ANALYZING..." : "RUN PROMO AI"}
            </button>
            <button 
              onClick={handleEvacuate} 
              disabled={evacuating}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold flex items-center gap-2 transition-colors disabled:opacity-50 shadow-[0_0_15px_rgba(220,38,38,0.5)]"
            >
              <AlertTriangle className="w-5 h-5" />
              {evacuating ? "TRIGGERING..." : "EMERGENCY EVACUATE"}
            </button>
            <button onClick={fetchState} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
              <RefreshCw className="w-5 h-5 text-slate-400" />
            </button>
          </div>
        </div>

        <div className="max-w-7xl mx-auto w-full">
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <div className="text-slate-400 text-sm font-medium mb-1">Stadium Occupancy</div>
              <div className="text-3xl font-bold text-white flex items-center gap-2">
                <Users className="w-6 h-6 text-emerald-500" />
                {state?.crowd_map.total_occupancy_pct}%
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <div className="text-slate-400 text-sm font-medium mb-1">Active Incidents</div>
              <div className="text-3xl font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-6 h-6 text-amber-500" />
                {allIncidents.length}
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <div className="text-slate-400 text-sm font-medium mb-1">Critical Issues</div>
              <div className="text-3xl font-bold text-rose-500 flex items-center gap-2">
                <ShieldAlert className="w-6 h-6 text-rose-500" />
                {criticalIncidents.length}
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
              <div className="text-slate-400 text-sm font-medium mb-1">Acoustic Peak</div>
              <div className="text-3xl font-bold text-purple-400 flex items-center gap-2 tracking-wider">
                <Volume2 className="w-6 h-6 text-purple-500" />
                {state?.crowd_map.sections.some(s => s.acoustic_status === 'CHEERING' || s.acoustic_status === 'TENSE') ? 'LOUD' : 'NORMAL'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Predictive Alerts */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col min-h-[300px]">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-indigo-400" />
                Predictive Alerts
              </h2>
              <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                {predictiveAlerts.length === 0 ? (
                  <div className="text-slate-500 text-sm text-center py-4">No imminent congestion detected.</div>
                ) : (
                  predictiveAlerts.map(alert => (
                    <div key={alert.section_id} className="bg-indigo-950/30 border border-indigo-900/50 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-semibold text-indigo-300">{alert.section_name}</span>
                        <div className="flex items-center gap-2">
                          {alert.acoustic_status && (
                            <span className="text-[10px] font-mono bg-purple-900/50 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 flex items-center gap-1 uppercase tracking-wider">
                              <Volume2 className="w-3 h-3" />
                              {alert.acoustic_status}
                            </span>
                          )}
                          <span className="text-xs font-mono bg-indigo-900 text-indigo-200 px-2 py-0.5 rounded">
                            {alert.density_pct.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-indigo-200/70">
                        Predicted to hit 85% capacity in <span className="font-bold text-white">{alert.predicted_mins_to_85} mins</span>.
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Active Incidents */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col min-h-[300px]">
              <h2 className="text-lg font-semibold text-white mb-4">Live Incidents</h2>
              <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                {allIncidents.length === 0 ? (
                  <div className="text-slate-500 text-sm text-center py-4">All clear.</div>
                ) : (
                  allIncidents.map(inc => (
                    <div key={inc.id} className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-semibold text-slate-300 capitalize">{inc.category}</span>
                        <span className={`text-xs font-mono px-2 py-0.5 rounded ${inc.severity === 'critical' ? 'bg-rose-900 text-rose-200' : inc.severity === 'high' ? 'bg-amber-900 text-amber-200' : 'bg-slate-700 text-slate-300'}`}>
                          {inc.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-400 line-clamp-2">
                        {inc.description}
                      </p>
                      <button 
                        onClick={() => setSelectedIncident(inc)}
                        className="mt-3 text-xs w-full bg-slate-700/50 hover:bg-slate-600 text-slate-300 py-1.5 px-3 rounded flex items-center justify-center gap-2 transition-colors border border-slate-600/50 hover:border-slate-500"
                      >
                        <InfoIcon className="w-3 h-3" /> View Details & Dispatch
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Action Buttons */}
      <div className="fixed bottom-8 right-8 flex flex-col gap-4 z-50">
        <button 
          onClick={() => setMapOpen(!mapOpen)} 
          className="w-14 h-14 bg-emerald-600 rounded-full flex items-center justify-center shadow-lg hover:bg-emerald-500 hover:scale-110 transition-all"
          title="Open Crowd Heatmap"
        >
          <MapIcon className="w-6 h-6 text-white"/>
        </button>
        <button 
          onClick={() => setChatOpen(!chatOpen)} 
          className="w-14 h-14 bg-blue-600 rounded-full flex items-center justify-center shadow-lg hover:bg-blue-500 hover:scale-110 transition-all"
          title="Open AI Copilot"
        >
          <MessageCircle className="w-6 h-6 text-white"/>
        </button>
      </div>

      {/* Floating Chat Overlay */}
      <AnimatePresence>
        {chatOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-28 right-8 w-[400px] h-[600px] bg-slate-900/95 backdrop-blur-xl border border-slate-700 rounded-2xl shadow-[0_0_40px_rgba(0,0,0,0.5)] flex flex-col z-50 overflow-hidden"
          >
            <div className="p-4 border-b border-slate-800 bg-slate-900/80 flex justify-between items-center">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <ShieldAlert className="w-5 h-5 text-blue-500" />
                  AI Copilot
                </h2>
                <p className="text-xs text-slate-400">Ask questions about the stadium state</p>
              </div>
              <button onClick={() => setChatOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <XIcon className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatHistory.length === 0 && (
                <div className="text-center text-slate-500 text-sm mt-10">
                  <ShieldAlert className="w-8 h-8 mx-auto mb-3 opacity-50" />
                  <p>I'm your AI Copilot.</p>
                  <p className="mt-1 text-xs opacity-70">Try asking: "What are our biggest risks right now?"</p>
                </div>
              )}
              {chatHistory.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-2 ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-200'}`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] rounded-2xl px-4 py-2 bg-slate-800 text-slate-200">
                    <Loader2 className="w-4 h-4 animate-spin opacity-50" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 border-t border-slate-800 bg-slate-900/80">
              <form 
                onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                className="flex relative"
              >
                <input
                  type="text"
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  placeholder="Ask Copilot..."
                  className="w-full bg-slate-800 border-none rounded-full pl-4 pr-12 py-3 text-sm text-white focus:ring-1 focus:ring-blue-500 focus:outline-none"
                />
                <button 
                  type="submit" 
                  disabled={!chatInput.trim() || chatLoading}
                  className="absolute right-1 top-1 bottom-1 w-10 flex items-center justify-center bg-blue-600 rounded-full text-white disabled:opacity-50 hover:bg-blue-500 transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Map Overlay */}
      <AnimatePresence>
        {mapOpen && (
          <motion.div 
            initial={{ opacity: 0, backdropFilter: "blur(0px)" }}
            animate={{ opacity: 1, backdropFilter: "blur(8px)" }}
            exit={{ opacity: 0, backdropFilter: "blur(0px)" }}
            className="fixed inset-0 bg-slate-950/60 z-40 flex items-center justify-center p-8"
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="relative w-full h-full flex flex-col items-center justify-center"
            >
              <div className="absolute top-6 left-6 sm:top-10 sm:left-10 flex items-center gap-3 z-10 bg-slate-900/80 p-4 rounded-xl backdrop-blur-md border border-slate-800">
                <MapIcon className="w-8 h-8 text-emerald-400" />
                <div>
                  <h2 className="text-xl font-bold text-white leading-tight">Live Crowd Heatmap</h2>
                  <p className="text-sm text-slate-400 mt-1">Real-time occupancy density</p>
                </div>
              </div>
              
              <button 
                onClick={() => setMapOpen(false)} 
                className="absolute top-6 right-6 sm:top-10 sm:right-10 z-10 p-3 bg-slate-800/80 hover:bg-slate-700 text-slate-300 rounded-full backdrop-blur-md transition-colors border border-slate-700"
              >
                <XIcon className="w-6 h-6" />
              </button>

              <div className="w-full h-full flex items-center justify-center scale-95 origin-center">
                <StadiumMap heatmapData={heatmapData} />
              </div>
              
              {/* Heatmap Legend */}
              <div className="absolute bottom-8 right-8 bg-slate-900/80 backdrop-blur-md border border-slate-800 p-4 rounded-xl flex items-center gap-4">
                <span className="text-sm text-slate-400 font-medium">Density:</span>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-emerald-500 opacity-60"></div>
                  <span className="text-xs text-slate-300">{'< 60%'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-amber-500 opacity-70"></div>
                  <span className="text-xs text-slate-300">60-84%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-rose-500 opacity-80"></div>
                  <span className="text-xs text-slate-300">{'>= 85%'}</span>
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
            className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4"
          >
            <motion.div
              initial={{ scale: 0.95, y: 10 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 10 }}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full shadow-2xl relative overflow-hidden"
            >
              <button 
                onClick={() => setSelectedIncident(null)}
                className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors p-2"
              >
                <XIcon className="w-5 h-5" />
              </button>

              <div className="flex items-center gap-3 mb-6 pr-8">
                <div className={`p-2 rounded-lg ${selectedIncident.severity === 'critical' ? 'bg-rose-500/20 text-rose-400' : selectedIncident.severity === 'high' ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-700/50 text-slate-400'}`}>
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white capitalize">{selectedIncident.category || 'General'} Incident</h3>
                  <p className="text-sm text-slate-400 flex items-center gap-2 mt-1">
                    Status: <span className="text-emerald-400 uppercase text-[10px] font-bold px-1.5 py-0.5 bg-emerald-500/10 rounded">{selectedIncident.status}</span>
                  </p>
                </div>
              </div>

              <div className="space-y-6">
                <div>
                  <h4 className="text-xs uppercase text-slate-500 font-bold mb-2">Reporter Details</h4>
                  <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50 flex items-start gap-3">
                    <UserCircle2 className="w-8 h-8 text-slate-400 mt-1" />
                    <div>
                      <p className="text-sm text-white font-medium">Carlos Rivera (Fan App)</p>
                      <p className="text-xs text-slate-400 mt-1">Location: Section N101, Row 1, Seat 1</p>
                      <p className="text-sm text-slate-300 mt-2 p-2 bg-slate-900/50 rounded italic border-l-2 border-slate-600">
                        "{selectedIncident.description}"
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xs uppercase text-slate-500 font-bold mb-2">Dispatched Volunteer</h4>
                  <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700/50 flex items-start gap-3">
                    <UserCheck className="w-8 h-8 text-blue-400 mt-1" />
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <p className="text-sm text-white font-medium">{selectedIncident.volunteer_name || "Volunteer Team Alpha"}</p>
                        <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded uppercase font-bold">{selectedIncident.volunteer_name ? "Assigned" : "Pending"}</span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">Status: {selectedIncident.volunteer_name ? "Assessing situation..." : "Assigning volunteer..."}</p>
                    </div>
                  </div>
                </div>

                <div className="border-t border-slate-800 pt-6">
                  <h4 className="text-xs uppercase text-slate-500 font-bold mb-3 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-emerald-400" />
                    AI Auto-Resolution Status
                  </h4>
                  <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-4">
                    <p className="text-sm text-emerald-200 leading-relaxed">
                      <span className="font-bold text-emerald-400">Automated Dispatch Complete:</span> The AI Copilot has already routed the nearest volunteer team to this row. The regional medical team has been pre-notified of the situation on their zone dashboards.
                    </p>
                    <div className="mt-4 flex gap-3">
                      <button 
                        onClick={() => setSelectedIncident(null)}
                        className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 py-2 rounded-lg text-sm font-medium transition-colors border border-slate-700"
                      >
                        Close Details
                      </button>
                      <button 
                        onClick={async () => { 
                          try {
                            await resolveIncident(selectedIncident.id);
                            setSelectedIncident(null); 
                            fetchState(); // Refresh dashboard
                          } catch (err) {
                            console.error("Failed to resolve incident", err);
                          }
                        }}
                        className="flex-1 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 py-2 rounded-lg text-sm font-bold transition-colors border border-emerald-500/30"
                      >
                        Force Resolve
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
