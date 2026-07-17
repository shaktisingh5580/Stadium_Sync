import { apiClient } from './client';

export interface Incident {
  id: string;
  severity: string;
  category: string;
  status: string;
  description: string;
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

export async function sendAdminChat(message: string, history: any[] = []): Promise<{ message: string }> {
  const response = await apiClient.post<{ message: string }>('/admin/chat', { message, history });
  return response.data;
}

export async function triggerEvacuation(hazardZone?: string): Promise<{ status: string }> {
  const response = await apiClient.post<{ status: string }>('/admin/evacuate', { hazard_zone: hazardZone });
  return response.data;
}

export async function evaluatePromotions(): Promise<{ status: string, promotion?: any, message?: string }> {
  const response = await apiClient.post('/admin/evaluate-promotions');
  return response.data;
}

export async function resolveIncident(incidentId: string): Promise<{ success: boolean, message: string }> {
  const response = await apiClient.post<{ success: boolean, message: string }>(`/incidents/${incidentId}/resolve`);
  return response.data;
}
