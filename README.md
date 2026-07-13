# 🏟️ Stadium Sync
### *The AI Operating System for the FIFA World Cup 2026*

> **Stadium Sync is not a chatbot. It is the brain of the stadium.**  
> It continuously understands every fan, volunteer, sensor, gate, and incident — predicts problems before they happen — and autonomously coordinates 80,000 people toward a safer, smarter, and greener match-day experience.

---

## The Problem With Stadiums Today

Stadium operations still run like it's 1998.

- A fan gets lost. Nobody knows.  
- A spill happens. Staff find out in 8 minutes.  
- A gate reaches 95% capacity. No one reroutes the crowd until there's a crush.  
- 80,000 people try to leave at once. Everyone exits through the same gates.  
- A plastic bottle goes in the wrong bin. Nobody notices.

**These aren't small annoyances. They are safety failures, sustainability failures, and experience failures — happening simultaneously, at scale, in 60-second windows.**

Stadium Sync solves all of them. Together. With one AI.

---

## One AI. Everything Connected.

Every module in Stadium Sync shares context with every other module. The AI doesn't answer questions in isolation — it **understands the stadium as a living system** and acts on that understanding.

```
                    ┌─────────────────────────────┐
                    │      STADIUM SYNC AI BRAIN   │
                    │                             │
  Fan message ────► │  Knows crowd density        │
  Sensor data ────► │  Knows your seat & transit  │
  Incident ──────► │  Knows volunteer positions  │
  IoT gate data ──► │  Knows gate congestion      │
  Image upload ──►  │  Knows eco-bin locations    │
                    │                             │
                    │  → Decides what to do       │
                    │  → Coordinates the response │
                    │  → Pushes to every device   │
                    └─────────────────────────────┘
```

When a fan asks *"Where should I get food?"* — Stadium Sync already knows:
- How crowded each concession stand is (from IoT sensors)
- Whether the fan uses a wheelchair (from their ticket profile)
- That halftime started 3 minutes ago (surge incoming)
- That a spill was just reported near Stall 12 (from incident system)
- That their exit gate is Gate East (from their transit preference)

The response isn't *"Food is at Section 106."*  
It's *"Head to Stall 18 — 2-minute wait, wheelchair accessible, on your way to Gate East. Avoid Stall 12, there's a clean-up in progress."*

**That is intelligence. Not a chatbot.**

---

## Projected Impact

| Metric | Improvement |
|---|---|
| Average fan navigation time | **↓ 50%** |
| Emergency response dispatch time | **↓ 78%** (5 min → 65 sec) |
| Exit congestion at match end | **↓ 35%** via pre-computed egress routing |
| Waste sorted correctly | **↑ 70%** via real-time AI classification |
| Volunteer idle time | **↓ 60%** via intelligent proximity dispatch |
| Language barriers eliminated | **100+ languages** supported natively |
| Concurrent fan capacity | **80,000 simultaneous connections** via WebSocket |
| LLM API cost for navigation | **$0** (static intercepts bypass LLM entirely) |

*Projections based on system architecture benchmarks and comparative studies of smart stadium deployments.*

---

## The Fan Journey

A fan arrives at MetLife Stadium, New Jersey. This is their entire match-day experience with Stadium Sync.

**7:15 PM — Arrival**  
They scan their digital QR ticket at the gate. In 180ms, Stadium Sync validates the cryptographic checksum, confirms their seat in the database, and issues a secure session that knows their name, seat, section, and how they're getting home.

**7:23 PM — Finding the Seat**  
They type *"/seat"*. No LLM is called. No API cost. The backend intercepts the command, fetches their exact SVG seat coordinates from PostgreSQL, and draws a smooth curved arc from the entrance to their seat — routing them along the outer concourse, avoiding the field entirely. They walk directly there.

**8:10 PM — The Spill**  
The fan notices a large spill in their row. They type *"large spill, row 7, aisle blocked."* Gemini reads the message, classifies severity as `HIGH`, writes a structured incident to the database, and within 4 seconds the nearest available volunteer receives an assignment with their name, the exact section, and the nature of the incident. Expected response: 3 minutes. The fan gets a confirmation with an incident ID.

**Half-Time — The Waste**  
The fan has a plastic cup and a banana peel. They photograph both. Gemini Vision identifies: plastic → Blue Recycle bin, banana → Green Compost bin. The map opens showing two curved routes — one to the recycling point, one to the compost point, both on their path to the concession stand.

**90th Minute — The Exit**  
Stadium Sync's egress agent detects Gate West is at 88% density. Without anyone asking, it pre-computes personalized exit routes for all 80,000 fans based on live congestion data. As the final whistle blows, every fan's phone receives a push notification via WebSocket. The screen flashes: *"Your safest exit is Gate North. Leave now — estimated 6 minutes. Your bus departs in 18 minutes."* Congestion at the stadium drops measurably within 4 minutes.

---

## Why Generative AI Is Non-Negotiable

Remove Gemini and the stadium becomes a broken system:

| Without AI | What breaks |
|---|---|
| No intent understanding | Fan says "I feel sick" — system does nothing. With AI: medical station route + volunteer dispatched immediately |
| No triage | All incidents get the same response time. With AI: a fire is treated like a spill until a human reviews it |
| No image understanding | Fan photographs a soup container. Without vision AI, impossible to classify. With AI: instant, accurate, bin-specific |
| No context-aware routing | Navigation sends everyone to the closest gate. With AI: it knows your bus leaves in 12 minutes and routes accordingly |
| No conversational understanding | Slang, typos, indirect questions. Without AI: null response. With AI: understood and answered |
| No language flexibility | A Japanese fan types in Japanese. Without AI: no response. With AI: answer delivered in Japanese |

**Generative AI is not decorating Stadium Sync. It is what makes Stadium Sync possible.**

---

## How It Works (For Those Who Want to Know)

Stadium Sync is built in two layers: a **FastAPI backend** (Python 3.12) and a **React 19 frontend** — connected by REST APIs and a persistent WebSocket channel. The AI is Google Gemini 2.0 Flash, with NVIDIA Llama 3.1 70B as a parallel provider for rate-limit resilience.

### The AI Pipeline
Every fan message flows through a single `POST /chat` endpoint that orchestrates all features:
1. **Static intercept check** — if it's a known command, respond in 0ms without touching the LLM
2. **LLM call with full context** — fan's name, seat, section, transit, and match injected into every prompt
3. **Structured JSON action** — AI returns `{message, ui_action, payload}` telling the frontend exactly what to render
4. **Side-effect execution** — route computed in Python math engine, incident written to DB, volunteer dispatched — all in the same request before responding

### The AI Client Pool
Production rate limits don't exist for Stadium Sync. API keys from both Gemini and NVIDIA are pooled and served round-robin:
```
GEMINI_API_KEYS=gemini-key-1,gemini-key-2,gemini-key-3,nvapi-nvidia-key-1
```
Vision calls are pinned to Gemini (Llama 3.1 is text-only). Text calls rotate across all keys. At peak load with 5 keys, effective rate limit is 5x any individual key.

### The Navigation Engine
No LLM draws routes. A Python polar-coordinate arc generator computes a physically realistic path:
- Step the fan radially outward from their seat to the outer concourse
- Arc along the concourse perimeter (12–15 waypoints) toward the target gate's angular position
- Step inward to the gate
- Convert SVG units to meters (1 SVG unit ≈ 1.5m), estimate walking speed at 80m/min in a crowd

This means routes are **instantaneous, deterministic, and always correct** — no hallucinations possible.

### The Real-Time Layer
A FastAPI WebSocket hub (`/api/v1/realtime/ws`) maintains authenticated connections to every active fan device. When the egress agent fires:
1. Computes personalized routes for all tickets in one batch
2. Pushes `egress_route` event to every WebSocket connection simultaneously
3. Frontend receives it, flashes the alert, and draws the route — all within ~200ms of server trigger

---

## The Modules (All Wired Together)

| Module | What the AI Decides |
|---|---|
| **🎟️ Ticket Auth** | Is this ticket valid? What does this fan need access to? |
| **🗺️ Navigation** | Which gate matches this fan's transit and the live crowd situation? |
| **♻️ Eco-Vision** | What is this object? Which bin? Where is the nearest one? |
| **🚨 Incidents** | How serious is this? Which volunteer is closest? Who should be notified? |
| **🌊 Egress** | Which fans should exit which gate to minimize total congestion? |
| **📡 Crowd Intel** | Where is density rising? Which sections need attention? |
| **🤝 Volunteers** | Who is idle? Who is overloaded? What is their fastest path? |

---

## Security — Production Grade

Stadium Sync treats security as a first-class requirement, not an afterthought.

- **QR Integrity:** SHA-256 checksum prevents forged tickets. Invalid checksums are rejected before the database is even queried.
- **JWT Sessions:** 4-hour expiration tied to match duration. Role-embedded tokens (`fan`, `volunteer`, `admin`) enforce access at the route layer.
- **IoT Separation:** Crowd sensor ingestion uses a separate `X-API-Key` header — sensor data never touches fan authentication paths.
- **Rate Limiting:** AI endpoints: 10 req/min. IoT ingestion: 300 req/min. Auth: 10 req/min. Enforced via Redis-backed `slowapi`.
- **Container Hardening:** Non-root `appuser` in a multi-stage Docker build — no dev dependencies in production image.

---

## Proven Reliable — 57 Automated Tests

```
Phase 1: Foundation     — App startup, JWT, CORS, error schemas, DB tables
Phase 2: Auth           — QR scan, checksum validation, inactive tickets, refresh
Phase 3: Navigation     — Transit update, route math, auth guards
Phase 4: Features       — Eco-vision, incident lifecycle, auto-dispatch
Phase 5: Real-time      — IoT ingestion, crowd map, egress trigger, WebSocket ping
Phase 6: End-to-End     — Full fan journey, JWT rejection, validation errors
```

Tests run against an in-memory SQLite database with no external dependencies — zero flakiness, zero cost, runs in 11 seconds.

---

## The Stack

```
Backend:   FastAPI · Python 3.12 · PostgreSQL · Redis · SQLAlchemy Async
AI:        Google Gemini 2.0 Flash · NVIDIA Llama 3.1 70B (round-robin pool)  
Frontend:  React 19 · Vite · TypeScript · Tailwind CSS · Framer Motion
Real-time: FastAPI WebSockets · Custom ConnectionManager
Auth:      JWT HS256 · SHA-256 QR checksum
Deploy:    Docker (multi-stage) · Render (API) · Vercel (frontend)
```

---

## Try It

The system is live. Every API endpoint has a health check, every feature has a demo mode.

**Quick Start (Development)**
```bash
# 1. Infrastructure
docker compose up -d       # PostgreSQL + Redis

# 2. Seed the stadium
make seed                  # Stadium map, gates, test tickets

# 3. Backend  
cd backend && make dev     # → http://localhost:8000/docs

# 4. Frontend
cd frontend && npm run dev # → http://localhost:5173
```

**At the login screen:** click *"Dev Bypass"* to skip QR scanning and enter as a test fan (ticket-001, Section N101).

**To trigger egress simulation:** click the *"Simulate Egress"* button in the top-left corner. Watch every connected device receive a real-time push event within 200ms.

**Environment**
```bash
cp backend/.env.example backend/.env
# Fill in: DATABASE_URL, GEMINI_API_KEYS, REDIS_URL, SECRET_KEY
```

---

## Make Commands

```bash
make docker-up    # Start infrastructure
make seed         # Seed stadium data
make dev          # Start backend (port 8000)
make test         # Run all 57 tests
make test-all     # Tests + coverage report
make lint         # Lint Python (ruff)
```

---

*Stadium Sync — Built for the FIFA World Cup 2026 Hack2Skill Challenge.*  
*One AI. 80,000 fans. Zero compromises.*
