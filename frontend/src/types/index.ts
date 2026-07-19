/**
 * ===============================================================================
 * File: frontend/src/types/index.ts
 * Purpose: TypeScript interfaces - defines all data structures across app 
 *          (Fan, Incident, Route, CrowdData, etc.).
 * Architecture: Single source of truth for data shapes. Matches backend 
 *               Pydantic schemas for type-safe API communication.
 * Inputs: None (type definitions).
 * Outputs: Type definitions imported throughout app for compile-time safety.
 * Hackathon Vertical: Code Quality
 * ===============================================================================
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
