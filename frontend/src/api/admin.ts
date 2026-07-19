/**
 * ============================================================================
 * File: frontend/src/api/admin.ts
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Admin / Organizer API Functions.
 *
 * Provides typed API calls for the Organizer Command Center (AdminDashboard):
 * - getAdminState — Fetches the digital twin state (incidents + crowd heatmap + predictions)
 * - sendAdminChat — Chats with the Admin Copilot AI using live stadium context
 * - triggerEvacuation — Broadcasts an emergency evacuation to all connected fans
 * - evaluatePromotions — AI-driven flash sale targeting based on crowd density
 * - resolveIncident — Marks an incident as resolved
 * - triggerCVWebhook — Simulates a Computer Vision edge-node event
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
