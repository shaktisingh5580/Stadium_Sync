import React from 'react';
import './StadiumMap.css';

interface StadiumMapProps {
  className?: string;
  selectedSection?: string;
  onSectionClick?: (sectionId: string) => void;
  fanSeat?: { x: number, y: number };
  egressRoute?: { x: number, y: number }[];
}

export const StadiumMap: React.FC<StadiumMapProps> = ({ className, selectedSection, onSectionClick, fanSeat, egressRoute }) => {
  return (
    <div className={`relative w-full h-full max-w-[800px] max-h-[800px] aspect-square drop-shadow-[0_0_25px_rgba(34,197,94,0.1)] ${className || ''}`}>
      
{/*
  Stadium Sync — Top-Down Stadium SVG
  ViewBox: 0 0 800 800 (centered at 400, 400)
  
  Geometry:
    Outer boundary circle: r=375
    Seating sections ring: r=240 (inner) to r=350 (outer)
    Concourse walkway ring: r=185 to r=240
    Pitch: 160×260 rectangle centered at (400, 400)
  
  Sections are arc segments with 35° spans, separated by 16° gate gaps
  and 4° inter-section gaps. 8 sections total, arranged in pairs:
    N1/N2 (north), E1/E2 (east), S1/S2 (south), W1/W2 (west)
  
  All element IDs follow the pattern:
    section-{n1|n2|e1|e2|s1|s2|w1|w2}
    gate-{north|south|east|west}
    amenity-{type}-{location}
    route-overlay, heatmap-overlay, fan-marker
*/}
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <defs>
    {/* ═══ FILTERS ═══ */}
    <filter id="glow-green" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="glow-amber" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
    <filter id="glow-pulse" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>

    {/* ═══ GRADIENTS ═══ */}
    <radialGradient id="stadium-bg" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stopColor="#1e293b"/>
      <stop offset="70%"  stopColor="#0f172a"/>
      <stop offset="100%" stopColor="#020617"/>
    </radialGradient>

    <linearGradient id="pitch-grass" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%"   stopColor="#166534"/>
      <stop offset="50%"  stopColor="#15803d"/>
      <stop offset="100%" stopColor="#166534"/>
    </linearGradient>

    <radialGradient id="gate-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stopColor="#fbbf24"/>
      <stop offset="100%" stopColor="#b45309"/>
    </radialGradient>

    {/* ═══ STYLES ═══ */}
    
  </defs>

  {/* ════════════════════════════════════════════════════════════
       LAYER 0: OUTER BACKGROUND (Deep space dark)
       ════════════════════════════════════════════════════════════ */}
  <rect x="0" y="0" width="800" height="800" fill="#020617"/>

  {/* ════════════════════════════════════════════════════════════
       LAYER 1: STADIUM STRUCTURE (Outer boundary + rings)
       ════════════════════════════════════════════════════════════ */}
  <g id="stadium-structure">
    {/* Outer glow ring */}
    <circle cx="400" cy="400" r="380" fill="none" stroke="#22c55e" strokeWidth="0.5" opacity="0.15"/>
    {/* Stadium body */}
    <circle cx="400" cy="400" r="375" fill="url(#stadium-bg)" stroke="#1e293b" strokeWidth="2"/>
    {/* Outer structural ring */}
    <circle cx="400" cy="400" r="355" fill="none" stroke="#334155" strokeWidth="0.5" opacity="0.4"/>
    {/* Section outer boundary marker */}
    <circle cx="400" cy="400" r="350" fill="none" stroke="#475569" strokeWidth="0.5" opacity="0.3"/>
    {/* Section inner boundary marker */}
    <circle cx="400" cy="400" r="240" fill="none" stroke="#475569" strokeWidth="0.5" opacity="0.3"/>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 2: CONCOURSE (Walkway rings + radial corridors)
       ════════════════════════════════════════════════════════════ */}
  <g id="concourse">
    {/* Main walkway ring */}
    <circle cx="400" cy="400" r="213" className="concourse-ring"/>
    <circle cx="400" cy="400" r="198" className="concourse-ring" opacity="0.4"/>

    {/* Cardinal corridors (through gate gaps to the pitch) */}
    <line x1="400" y1="270" x2="400" y2="50"  className="corridor-line"/>
    <line x1="400" y1="530" x2="400" y2="750" className="corridor-line"/>
    <line x1="530" y1="400" x2="750" y2="400" className="corridor-line"/>
    <line x1="270" y1="400" x2="50"  y2="400" className="corridor-line"/>

    {/* Diagonal corridors (between section pairs) */}
    <line x1="313" y1="313" x2="175" y2="175" className="corridor-line" opacity="0.5"/>
    <line x1="487" y1="313" x2="625" y2="175" className="corridor-line" opacity="0.5"/>
    <line x1="487" y1="487" x2="625" y2="625" className="corridor-line" opacity="0.5"/>
    <line x1="313" y1="487" x2="175" y2="625" className="corridor-line" opacity="0.5"/>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 3: SEATING SECTIONS (8 arc segments)
       
       Geometry:
         Center: (400, 400), OuterR: 350, InnerR: 240
         Gate gap: ±8° at each cardinal direction
         Section span: 35° each, 4° gap between pairs
         
       Arc path template:
         M outerStart A 350 350 0 0 1 outerEnd
         L innerEnd   A 240 240 0 0 0 innerStart Z
       ════════════════════════════════════════════════════════════ */}
  <g id="sections">
    {/* N1 — North-West section (227° → 262°) */}
    <path id="section-n1" className={`section ${selectedSection === "section-n1" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-n1")}
          d="M 161.3 144.0
             A 350 350 0 0 1 351.3 53.4
             L 366.6 162.3
             A 240 240 0 0 0 236.3 224.5 Z"/>

    {/* N2 — North-East section (278° → 313°) */}
    <path id="section-n2" className={`section ${selectedSection === "section-n2" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-n2")}
          d="M 448.7 53.4
             A 350 350 0 0 1 638.7 144.0
             L 563.7 224.5
             A 240 240 0 0 0 433.4 162.3 Z"/>

    {/* E1 — East-Upper section (317° → 352°) */}
    <path id="section-e1" className={`section ${selectedSection === "section-e1" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-e1")}
          d="M 656.0 161.3
             A 350 350 0 0 1 746.6 351.3
             L 637.7 366.6
             A 240 240 0 0 0 575.5 236.3 Z"/>

    {/* E2 — East-Lower section (8° → 43°) */}
    <path id="section-e2" className={`section ${selectedSection === "section-e2" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-e2")}
          d="M 746.6 448.7
             A 350 350 0 0 1 656.0 638.7
             L 575.5 563.7
             A 240 240 0 0 0 637.7 433.4 Z"/>

    {/* S2 — South-East section (47° → 82°) */}
    <path id="section-s2" className={`section ${selectedSection === "section-s2" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-s2")}
          d="M 638.7 656.0
             A 350 350 0 0 1 448.7 746.6
             L 433.4 637.7
             A 240 240 0 0 0 563.7 575.5 Z"/>

    {/* S1 — South-West section (98° → 133°) */}
    <path id="section-s1" className={`section ${selectedSection === "section-s1" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-s1")}
          d="M 351.3 746.6
             A 350 350 0 0 1 161.3 656.0
             L 236.3 575.5
             A 240 240 0 0 0 366.6 637.7 Z"/>

    {/* W2 — West-Lower section (137° → 172°) */}
    <path id="section-w2" className={`section ${selectedSection === "section-w2" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-w2")}
          d="M 144.0 638.7
             A 350 350 0 0 1 53.4 448.7
             L 162.3 433.4
             A 240 240 0 0 0 224.5 563.7 Z"/>

    {/* W1 — West-Upper section (188° → 223°) */}
    <path id="section-w1" className={`section ${selectedSection === "section-w1" ? "selected" : ""}`} onClick={() => onSectionClick?.("section-w1")}
          d="M 53.4 351.3
             A 350 350 0 0 1 144.0 161.3
             L 224.5 236.3
             A 240 240 0 0 0 162.3 366.6 Z"/>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 4: SECTION LABELS
       Positioned at midpoint angle of each section, at r=295
       ════════════════════════════════════════════════════════════ */}
  <g id="section-labels">
    <text x="273" y="168" className="section-label">N1</text>
    <text x="527" y="168" className="section-label">N2</text>
    <text x="632" y="293" className="section-label">E1</text>
    <text x="632" y="507" className="section-label">E2</text>
    <text x="527" y="632" className="section-label">S2</text>
    <text x="273" y="632" className="section-label">S1</text>
    <text x="168" y="507" className="section-label">W2</text>
    <text x="168" y="293" className="section-label">W1</text>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 5: FOOTBALL PITCH (centered at 400,400)
       Pitch: x=320 y=270 w=160 h=260
       ════════════════════════════════════════════════════════════ */}
  <g id="pitch">
    {/* Pitch surface */}
    <rect x="320" y="270" width="160" height="260" rx="2"
          fill="url(#pitch-grass)" stroke="#22c55e" strokeWidth="1.5" opacity="0.85"/>

    {/* Grass stripe pattern (alternating darker bands) */}
    <rect x="320" y="270" width="160" height="26" fill="#15803d" opacity="0.15"/>
    <rect x="320" y="322" width="160" height="26" fill="#15803d" opacity="0.15"/>
    <rect x="320" y="374" width="160" height="26" fill="#15803d" opacity="0.15"/>
    <rect x="320" y="426" width="160" height="26" fill="#15803d" opacity="0.15"/>
    <rect x="320" y="478" width="160" height="26" fill="#15803d" opacity="0.15"/>

    {/* ── Pitch Markings ── */}
    {/* Touchline border (outer rectangle) */}
    <rect x="325" y="275" width="150" height="250" rx="1" className="pitch-line-bold"/>

    {/* Halfway line */}
    <line x1="325" y1="400" x2="475" y2="400" className="pitch-line-bold"/>

    {/* Center circle */}
    <circle cx="400" cy="400" r="28" className="pitch-line"/>

    {/* Center mark */}
    <circle cx="400" cy="400" r="2.5" fill="rgba(255,255,255,0.45)"/>

    {/* Penalty area — Top */}
    <rect x="348" y="275" width="104" height="42" rx="1" className="pitch-line"/>
    {/* Goal area — Top */}
    <rect x="370" y="275" width="60" height="18" rx="1" className="pitch-line"/>
    {/* Penalty spot — Top */}
    <circle cx="400" cy="306" r="2" fill="rgba(255,255,255,0.4)"/>
    {/* Penalty arc — Top */}
    <path d="M 368 317 A 28 28 0 0 0 432 317" className="pitch-line"/>

    {/* Penalty area — Bottom */}
    <rect x="348" y="483" width="104" height="42" rx="1" className="pitch-line"/>
    {/* Goal area — Bottom */}
    <rect x="370" y="507" width="60" height="18" rx="1" className="pitch-line"/>
    {/* Penalty spot — Bottom */}
    <circle cx="400" cy="494" r="2" fill="rgba(255,255,255,0.4)"/>
    {/* Penalty arc — Bottom */}
    <path d="M 368 483 A 28 28 0 0 1 432 483" className="pitch-line"/>

    {/* Corner arcs */}
    <path d="M 325 283 A 8 8 0 0 1 333 275" className="pitch-line"/>
    <path d="M 467 275 A 8 8 0 0 1 475 283" className="pitch-line"/>
    <path d="M 475 517 A 8 8 0 0 1 467 525" className="pitch-line"/>
    <path d="M 333 525 A 8 8 0 0 1 325 517" className="pitch-line"/>

    {/* Goals (net outlines) */}
    <rect x="386" y="266" width="28" height="9" rx="2"
          fill="none" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5"/>
    <rect x="386" y="525" width="28" height="9" rx="2"
          fill="none" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5"/>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 6: GATES (4 amber circles at cardinal positions)
       Positioned on the outer boundary ring at r=370
       ════════════════════════════════════════════════════════════ */}
  <g id="gates">
    <g id="gate-north">
      <circle cx="400" cy="30" r="20" fill="url(#gate-glow)" stroke="#fbbf24" strokeWidth="2" filter="url(#glow-amber)"/>
      <text x="400" y="30" className="gate-letter">N</text>
      <text x="400" y="60" className="gate-name">GATE NORTH</text>
    </g>
    <g id="gate-south">
      <circle cx="400" cy="770" r="20" fill="url(#gate-glow)" stroke="#fbbf24" strokeWidth="2" filter="url(#glow-amber)"/>
      <text x="400" y="770" className="gate-letter">S</text>
      <text x="400" y="745" className="gate-name">GATE SOUTH</text>
    </g>
    <g id="gate-east">
      <circle cx="770" cy="400" r="20" fill="url(#gate-glow)" stroke="#fbbf24" strokeWidth="2" filter="url(#glow-amber)"/>
      <text x="770" y="400" className="gate-letter">E</text>
      <text x="740" y="400" className="gate-name" textAnchor="end">GATE EAST</text>
    </g>
    <g id="gate-west">
      <circle cx="30" cy="400" r="20" fill="url(#gate-glow)" stroke="#fbbf24" strokeWidth="2" filter="url(#glow-amber)"/>
      <text x="30" y="400" className="gate-letter">W</text>
      <text x="60" y="400" className="gate-name" textAnchor="start">GATE WEST</text>
    </g>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 7: AMENITIES (in the concourse ring, r≈195-215)
       Medical (blue), Eco-bins (green), Food (amber), Restrooms (purple)
       ════════════════════════════════════════════════════════════ */}
  <g id="amenities">
    {/* ── Medical Stations (Blue cross) ── */}
    <g className="amenity" id="amenity-medical-ne">
      <circle cx="510" cy="225" r="9" fill="#1e3a5f" stroke="#3b82f6" strokeWidth="1.5"/>
      <line x1="510" y1="220" x2="510" y2="230" stroke="white" strokeWidth="2" strokeLinecap="round"/>
      <line x1="505" y1="225" x2="515" y2="225" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    </g>
    <g className="amenity" id="amenity-medical-sw">
      <circle cx="290" cy="575" r="9" fill="#1e3a5f" stroke="#3b82f6" strokeWidth="1.5"/>
      <line x1="290" y1="570" x2="290" y2="580" stroke="white" strokeWidth="2" strokeLinecap="round"/>
      <line x1="285" y1="575" x2="295" y2="575" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    </g>

    {/* ── Eco / Recycle Bins (Green squares) ── */}
    <g className="amenity" id="amenity-eco-nw">
      <rect x="283" y="218" width="14" height="14" rx="3" fill="#14532d" stroke="#22c55e" strokeWidth="1.5"/>
      <text x="290" y="226" fill="#4ade80" fontSize="9" textAnchor="middle" dominantBaseline="central" fontWeight="bold">R</text>
    </g>
    <g className="amenity" id="amenity-eco-se">
      <rect x="503" y="568" width="14" height="14" rx="3" fill="#14532d" stroke="#22c55e" strokeWidth="1.5"/>
      <text x="510" y="576" fill="#4ade80" fontSize="9" textAnchor="middle" dominantBaseline="central" fontWeight="bold">R</text>
    </g>
    <g className="amenity" id="amenity-eco-e">
      <rect x="583" y="348" width="14" height="14" rx="3" fill="#14532d" stroke="#22c55e" strokeWidth="1.5"/>
      <text x="590" y="356" fill="#4ade80" fontSize="9" textAnchor="middle" dominantBaseline="central" fontWeight="bold">R</text>
    </g>
    <g className="amenity" id="amenity-eco-w">
      <rect x="203" y="438" width="14" height="14" rx="3" fill="#14532d" stroke="#22c55e" strokeWidth="1.5"/>
      <text x="210" y="446" fill="#4ade80" fontSize="9" textAnchor="middle" dominantBaseline="central" fontWeight="bold">R</text>
    </g>

    {/* ── Food Concessions (Amber circles) ── */}
    <g className="amenity" id="amenity-food-ne2">
      <circle cx="580" cy="260" r="7" fill="#78350f" stroke="#f59e0b" strokeWidth="1.5"/>
      <text x="580" y="261" fill="#fbbf24" fontSize="8" textAnchor="middle" dominantBaseline="central" fontWeight="bold">F</text>
    </g>
    <g className="amenity" id="amenity-food-sw2">
      <circle cx="220" cy="540" r="7" fill="#78350f" stroke="#f59e0b" strokeWidth="1.5"/>
      <text x="220" y="541" fill="#fbbf24" fontSize="8" textAnchor="middle" dominantBaseline="central" fontWeight="bold">F</text>
    </g>

    {/* ── Restrooms (Purple diamonds) ── */}
    <g className="amenity" id="amenity-restroom-n">
      <rect x="357" y="196" width="12" height="12" rx="2" fill="#3b0764" stroke="#a855f7" strokeWidth="1.5"
            transform="rotate(45, 363, 202)"/>
    </g>
    <g className="amenity" id="amenity-restroom-s">
      <rect x="431" y="590" width="12" height="12" rx="2" fill="#3b0764" stroke="#a855f7" strokeWidth="1.5"
            transform="rotate(45, 437, 596)"/>
    </g>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 8: HUD DECORATIONS (scan lines, compass, title)
       ════════════════════════════════════════════════════════════ */}
  <g id="hud-decorations" opacity="0.3">
    {/* Subtle crosshair at center */}
    <line x1="390" y1="400" x2="370" y2="400" stroke="#22c55e" strokeWidth="0.5"/>
    <line x1="410" y1="400" x2="430" y2="400" stroke="#22c55e" strokeWidth="0.5"/>
    <line x1="400" y1="390" x2="400" y2="370" stroke="#22c55e" strokeWidth="0.5"/>
    <line x1="400" y1="410" x2="400" y2="430" stroke="#22c55e" strokeWidth="0.5"/>

    {/* Corner brackets (HUD frame) */}
    {/* Top-left */}
    <path d="M 15 40 L 15 15 L 40 15" fill="none" stroke="#22c55e" strokeWidth="1"/>
    {/* Top-right */}
    <path d="M 760 15 L 785 15 L 785 40" fill="none" stroke="#22c55e" strokeWidth="1"/>
    {/* Bottom-right */}
    <path d="M 785 760 L 785 785 L 760 785" fill="none" stroke="#22c55e" strokeWidth="1"/>
    {/* Bottom-left */}
    <path d="M 40 785 L 15 785 L 15 760" fill="none" stroke="#22c55e" strokeWidth="1"/>
  </g>

  {/* ════════════════════════════════════════════════════════════
       LAYER 9: DYNAMIC OVERLAYS (controlled by React state)
       These groups are empty — React will populate them.
       ════════════════════════════════════════════════════════════ */}

  {/* Heatmap overlay: colored fills for each section based on density */}
  <g id="heatmap-overlay">
    {/* React renders <path> elements here matching section shapes
         with fill colors: green (low) → yellow (medium) → red (critical)
         and varying opacity based on density_pct */}
  </g>

  {/* Route overlay: dashed polyline from fan seat to assigned gate */}
    <g id="route-overlay">
    {egressRoute && egressRoute.length > 0 && (
      <polyline 
        points={egressRoute.map(p => `${p.x},${p.y}`).join(' ')} 
        className="route-path animate-pulse"
      />
    )}
  </g>

  {/* Fan seat marker: pulsing green dot at the fan's seat coordinates */}
    <g id="fan-marker">
    {fanSeat && (
      <circle className="seat-pulse" cx={fanSeat.x} cy={fanSeat.y} r="7" fill="#22c55e" filter="url(#glow-green)"/>
    )}
  </g>
</svg>

    </div>
  );
};
