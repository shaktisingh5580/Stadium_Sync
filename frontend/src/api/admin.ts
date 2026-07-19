/**
 * ===============================================================================
 * File: frontend/src/api/admin.ts
 * Purpose: Admin-specific API functions - getAdminState, sendAdminChat, 
 *          triggerEvacuation, uploadCVFrame.
 * Architecture: Wrapper functions for admin endpoints. Requires admin role 
 *               in JWT (enforced server-side).
 * Inputs: Admin query parameters, state request body.
 * Outputs: Admin response data (dashboard state, AI recommendations, etc.).
 * Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
 * ===============================================================================
 */

import { apiClient } from './client';

export interface Incident {
  id: string;
  severity: string;
  category: string;
  status: string;
  description: string;
  ticket_id?: string;
  location_description?: string;
  image_url?: string;
  volunteer_name?: string;
}

export interface ChatMessage {
  role: string;
  content: string;
}

export interface Promotion {
  message?: string;
  [key: string]: unknown;
}

export interface CrowdSection {
  section_id: string;
  section_name: string;
  density_pct: number;
  density_level: string;
  timestamp: string;
  predicted_mins_to_85: number | null;
  trend: string | null;
  sentiment_score: number | null;
  acoustic_status: string | null;
}

export interface CrowdMap {
  stadium_id: string;
  sections: CrowdSection[];
  timestamp: string;
  total_occupancy_pct: number;
}

export interface AdminState {
  stadium_id: string;
  incidents: Incident[];
  crowd_map: CrowdMap;
  error?: string;
}

export async function getAdminState(): Promise<AdminState> {
  const response = await apiClient.get<AdminState>('/admin/state');
  return response.data;
}

export async function sendAdminChat(message: string, history: ChatMessage[] = []): Promise<{ message: string }> {
  const response = await apiClient.post<{ message: string }>('/admin/chat', { message, history });
  return response.data;
}

export async function triggerEvacuation(hazardZone?: string): Promise<{ status: string }> {
  const response = await apiClient.post<{ status: string }>('/admin/evacuate', { hazard_zone: hazardZone });
  return response.data;
}

export async function evaluatePromotions(): Promise<{ status: string, promotion?: Promotion, message?: string }> {
  const response = await apiClient.post('/admin/evaluate-promotions');
  return response.data;
}

export async function resolveIncident(incidentId: string): Promise<{ success: boolean, message: string }> {
  const response = await apiClient.post<{ success: boolean, message: string }>(`/incidents/${incidentId}/resolve`);
  return response.data;
}

export async function triggerCVWebhook(data: {type: string, location: string, confidence: number, description: string, image_url?: string}): Promise<Record<string, unknown>> {
  const response = await apiClient.post(`/admin/cv-webhook`, data);
  return response.data;
}
