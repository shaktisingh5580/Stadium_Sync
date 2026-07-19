# Changelog

All notable changes to Stadium Sync are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] — 2026-07-19

### Added

#### Fan Experience
- **AI Concierge Chat** — Natural language navigation and assistance powered by Google Gemini 2.5 Flash with full fan context injection (seat, section, accessibility needs)
- **QR Ticket Authentication** — HMAC-SHA256 signed QR codes with JWT session issuance
- **Eco-Vision Waste Classification** — Camera-based AI waste categorization using Gemini Vision (multimodal)
- **Real-Time Egress Routes** — Personalized exit routes pushed via WebSocket, factoring in accessibility and nearest gate
- **Multilingual Support** — Gemini auto-detects language and responds natively (Hindi, Spanish, French, Arabic, etc.)
- **Indoor Navigation** — SVG-based interactive stadium map with animated route overlays and POI navigation

#### Volunteer Operations
- **AI-Powered Incident Triage** — Gemini classifies severity, category, and suggests response actions as structured JSON
- **Proximity-Based Volunteer Dispatch** — Auto-assignment to nearest available volunteer based on section coordinates
- **Real-Time Coordination** — WebSocket-based alert delivery for critical incidents

#### Organizer Intelligence
- **Digital Twin Heatmap** — Live crowd density visualization with linear regression congestion predictions
- **Admin AI Copilot** — Gemini chat with full operational context (crowd levels, incidents, volunteer positions)
- **Emergency Evacuation Broadcast** — One-click evacuation alert pushed to all connected fans via WebSocket
- **CV Webhook Integration** — Computer Vision edge-node analysis using Gemini Vision for automated safety alerts
- **Flash Sales Engine** — AI-driven vendor promotions targeted at underutilized stadium sections

### Infrastructure
- FastAPI async backend with Python 3.12 and Uvicorn
- React 19 frontend with TypeScript (strict mode), Vite, and TailwindCSS
- Render Docker deployment with render.yaml IaC blueprint
- Multi-stage Docker build with non-root execution
- PostgreSQL (Neon Serverless) / SQLite database with 15-table async ORM
- Redis caching with graceful in-memory fallback
- GitHub Actions CI pipeline with backend + frontend test suites

### Security
- HS256 JWT authentication with 4-hour match-duration expiry
- HMAC-SHA256 QR code integrity verification
- SlowAPI per-endpoint rate limiting (auth: 10/min, AI: 20/min, IoT: 300/min)
- Security headers middleware (CSP, X-Frame-Options, HSTS, X-Content-Type-Options)
- Pydantic input validation with length limits and regex patterns
- Production configuration validator (refuses unsafe settings)
- Non-root Docker container execution
- CORS explicit origin allowlist
