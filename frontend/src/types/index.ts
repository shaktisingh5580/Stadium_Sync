/**
 * ============================================================================
 * File: frontend/src/types/index.ts
 * Purpose: Frontend Application Module.
 * Architecture: React functional component/module in Vite ecosystem.
 * Inputs: Props, Context, or API data.
 * Outputs: Rendered DOM or functional logic.
 * Hackathon Vertical: Fan Experience & Navigation (FIFA 2026)
 * ============================================================================
 */
/**
 * Stadium Sync — Shared TypeScript Type Definitions.
 *
 * Defines the core domain interfaces used across the frontend:
 * - FanSession: Authenticated fan's ticket, seat, and accessibility profile
 * - Point2D / EgressRoute: SVG map coordinate system and egress path data
 * - EcoVisionResult: AI waste classification output (Gemini Vision)
 * - IncidentReport: Fan-reported issue with AI triage metadata
 * - CrowdSection / StadiumCrowdMap: Real-time crowd density heatmap data
 *
 * These types mirror the backend Pydantic schemas for end-to-end type safety.
 */
export interface FanSession {
  ticket_id?: string;
  ticketId: string;
  section: string;
  seatRow: string;
  seatNumber: number;
  holderName: string;
  matchId: string;
  transitMethod: string | null;
  needsAccessibility: boolean;
  token?: string;
  seat?: {
    id: string;
    section_id: string;
    section_name: string;
    section_type: string;
    row: string;
    number: number;
    svg_x: number;
    svg_y: number;
  };
}

export interface Point2D {
  x: number;
  y: number;
}

export interface EgressRoute {
  ticketId: string;
  transitMethod: string;
  targetGateId: string;
  targetGateName: string;
  distanceMeters: number;
  estimatedTimeMins: number;
  path: Point2D[];
  accessibilityFeatures?: string[] | null;
}

export interface EcoVisionResult {
  category: string;
  itemName: string;
  confidence: number;
  binColor: string;
  instructions: string;
  funFact: string;
}

export interface IncidentReport {
  id: string;
  ticketId: string;
  description: string;
  severity: string;
  category: string;
  status: string;
  estimatedResponseMins: number;
}

export interface CrowdSection {
  sectionId: string;
  sectionName: string;
  densityPct: number;
  densityLevel: string;
  predicted_mins_to_85?: number | null;
  trend?: string | null;
  sentiment_score?: number | null;
  acoustic_status?: string | null;
}

export interface StadiumCrowdMap {
  stadiumId: string;
  sections: CrowdSection[];
  totalOccupancyPct: number;
}
