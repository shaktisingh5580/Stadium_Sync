import { apiClient } from './client';
import type { EcoVisionResult } from '../types';

// Auth / Tokens
export const loginWithQR = async (qrPayload: string) => {
  const res = await apiClient.post('/auth/scan-ticket', { qr_payload: qrPayload });
  const token = res.data.data.token;
  localStorage.setItem('stadium_sync_token', token);
  return res.data.data;
};

export const fetchFanSession = async () => {
  const res = await apiClient.get('/auth/me');
  return res.data.data;
};

// Egress Navigation
export const updateTransitMethod = async (method: string) => {
  const res = await apiClient.post('/navigation/transit', { transit_method: method });
  return res.data;
};

export const fetchEgressRoute = async () => {
  const res = await apiClient.get('/navigation/route');
  return res.data.data; // { target_gate_name, distance_meters, estimated_time_mins, path }
};

export const triggerEgressSimulation = async () => {
  const res = await apiClient.post('/egress/trigger', {
    match_minute: 80,
    force: true
  });
  return res.data;
};

// Eco-Vision
export const classifyWasteImage = async (base64Image: string) => {
  const res = await apiClient.post('/eco-vision/classify', { 
    image_base64: base64Image,
    mime_type: 'image/jpeg' 
  });
  return res.data.data as EcoVisionResult;
};

// Incidents
export const reportIncident = async (description: string, imageBase64?: string) => {
  const payload: any = { description };
  if (imageBase64) {
    payload.image_base64 = imageBase64;
  }
  const res = await apiClient.post('/incidents/', payload);
  return res.data.data;
};

// Crowd / Real-time Map
export const fetchStadiumCrowdMap = async (stadiumId: string) => {
  const res = await apiClient.get(`/crowd/map/${stadiumId}`);
  return res.data.data;
};

// Agentic Chat
export const sendChatMessage = async (
  message: string, 
  history: Array<{ role: string; content: string }> = [],
  imageBase64?: string
) => {
  const payload: any = { message, history };
  if (imageBase64) {
    payload.image_base64 = imageBase64;
  }
  const res = await apiClient.post('/chat', payload);
  return res.data.data; // { message, ui_action, payload }
};
