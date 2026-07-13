export interface FanSession {
  ticketId: string;
  section: string;
  seatRow: string;
  seatNumber: number;
  holderName: string;
  matchId: string;
  transitMethod: string | null;
  token?: string;
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
}

export interface StadiumCrowdMap {
  stadiumId: string;
  sections: CrowdSection[];
  totalOccupancyPct: number;
}
