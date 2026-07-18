# 🏟️ STADIUM SYNC: THE AI OPERATING SYSTEM FOR FIFA WORLD CUP 2026

> **"Stadium Sync is not a chatbot. It is the centralized nervous system of the stadium."**
> 
> It continuously understands every fan, volunteer, sensor, gate, and incident — predicts problems before they happen — and autonomously coordinates 80,000 people toward a safer, smarter, and greener match-day experience.

---

## 📑 TABLE OF CONTENTS

1. [Executive Summary](#-executive-summary)
2. [The Problem with Legacy Stadiums](#-the-problem-with-legacy-stadiums)
3. [Core Features & Capabilities](#-core-features--capabilities)
4. [For the Judges: The Ultimate Demo Guide](#-for-the-judges-the-ultimate-demo-guide)
5. [The Fan Journey: A Walkthrough](#-the-fan-journey-a-walkthrough)
6. [Generative AI Integration](#-generative-ai-integration)
7. [Technical Architecture & System Design](#-technical-architecture--system-design)
8. [Project Structure](#-project-structure)
9. [Local Development Setup](#-local-development-setup)
10. [Database Schema & ERD](#-database-schema--erd)
11. [API Reference Documentation](#-api-reference-documentation)
12. [Real-Time WebSocket Protocol](#-real-time-websocket-protocol)
13. [Security & Authentication](#-security--authentication)
14. [Future Roadmap](#-future-roadmap)

---

## 🚀 EXECUTIVE SUMMARY

Stadium operations currently run in silos. Security doesn't talk to concessions; ticketing doesn't talk to crowd control. When 80,000 fans attend a FIFA World Cup match, these silos create dangerous bottlenecks, delayed emergency responses, and a frustrating fan experience.

**Stadium Sync** unifies all stadium operations into a single AI-driven platform. 
By utilizing **Google Gemini** for multimodal reasoning and **Nvidia NIM (Llama 3.1)** for lightning-fast NLP, the platform ingests data from fans (chat), staff (dashboards), and sensors (mocked IoT) to make instantaneous, global decisions.

---

## 🚨 THE PROBLEM WITH LEGACY STADIUMS

Stadiums today face three critical failures during mega-events like the World Cup:
1. **The Navigation Failure:** Fans get lost. Wayfinding signs are static and ignore live congestion.
2. **The Response Failure:** A medical emergency takes 8 minutes to reach dispatch because of hierarchical radio communication.
3. **The Egress Failure:** 80,000 people try to leave through the same 4 gates, creating crowd crushes.

**Stadium Sync solves all of them simultaneously.**

---

## 🌟 CORE FEATURES & CAPABILITIES

### 1. Agentic Fan Concierge (Generative AI)
- **Contextual Memory:** The AI is instantiated with state. It knows who you are, where you are sitting (e.g., Section N101, Row 1, Seat 1), and how you plan to leave the stadium.
- **Dynamic UI Rendering:** The chat is not just text. The AI leverages "UI Actions" to command the React frontend to render maps, image uploaders, or specific alert components based on the fan's intent.

### 2. Eco-Vision Waste Sorting (Multimodal AI)
- Fans can upload photos of their trash (e.g., a plastic bottle, a hot dog wrapper). 
- The AI instantly classifies the material (Compost, Recycle, Landfill) using **Gemini's Multimodal Vision capabilities** and routes the fan to the nearest correct bin using the SVG spatial map.

### 3. Automated Incident Triage & Dispatch
- Natural language reports from fans are parsed by **Llama 3.1** via Nvidia NIM.
- The AI autonomously determines the category (medical, security, maintenance) and severity (low, medium, high, critical).
- It writes the incident to the database and broadcasts it via WebSocket to the Admin Dashboard in milliseconds.

### 4. Real-Time Command Center (Admin Dashboard) & CV Webhooks
- A powerful React dashboard heavily utilizing WebSockets for real-time reactivity.
- Visualizes live stadium occupancy, predictive congestion alerts (e.g., "Section E2 will hit 85% capacity in 12 mins"), and active incidents.
- **Computer Vision (CV) Webhooks:** AI-driven simulation of real-time CCTV monitoring. It detects crowd density anomalies and fire/smoke risks, then automatically parses the telemetry (via a robust JSON-extraction layer) to alert the admin with contextualized severity warnings.

### 5. Dynamic Stadium Map & Intelligent Navigation
- **Interactive SVG Overlays:** Fans can view a dynamic map where points of interest (washrooms, medical, food) and specific seat sections are highlighted perfectly in sync with backend coordinates.
- **Flash Sales & Vendor Mapping:** When the admin triggers a flash sale, the fan app dynamically plots an animated, pulsating route directly from the fan's assigned seat to the specific concession stand (e.g., S203 Concessions).

### 6. Predictive Egress Routing
- Instead of everyone rushing the same gate, the system predicts congestion.
- The Admin can trigger "Egress" which pushes personalized, safe exit routes (with animated visual map lines) to every fan's phone simultaneously at the end of the match, balancing load across all physical gates.

---

## 👨‍⚖️ FOR THE JUDGES: THE ULTIMATE DEMO GUIDE

To fully experience the real-time, asynchronous capabilities of Stadium Sync, you **MUST** test the platform using **two separate browser windows side-by-side**. 

### 🖥️ Window Setup
1. **Window 1 (The Fan):** Open `https://stadium-sync-ea8o.vercel.app/`
2. **Window 2 (The Admin):** Open `https://stadium-sync-ea8o.vercel.app/?admin=true`

### 🧪 Step 1: Authentication (Fan Window)
- Click the **"Scan Ticket"** button.
- *Behind the scenes:* The backend validates a cryptographic checksum, fetches the fan's specific seat, and issues a JWT token. The fan is placed into the Chat interface.

### 🧪 Step 2: Spatial Awareness (Fan Window)
- Type: `/seat` or *"Where is my seat?"*
- *What happens:* The AI triggers a `SHOW_MAP` UI action. The interactive SVG stadium map renders a dynamic path from the entrance directly to the user's specific section.

### 🧪 Step 3: Eco-Vision Demo (Fan Window)
- Type: `/eco` or *"I have some trash, where do I put it?"*
- *What happens:* The AI requests an image upload. Upload an image of a plastic bottle. The Gemini Vision model will analyze the pixels, classify it as "Recycle", and guide you to the Blue bin.

### 🧪 Step 4: Real-Time Incident Reporting (Fan Window -> Admin Window)
- In the Fan Window, type: *"There is a huge spill of beer on the stairs in my section, someone might slip."*
- *What happens (Admin Window):* Look at your Admin Dashboard. Without refreshing the page, the incident instantly appears in the **Live Incidents** feed via WebSocket broadcast, complete with AI triage (High Severity).

### 🧪 Step 5: Closed-Loop AI Confirmation (Admin Window -> Fan Window)
- In the Admin Dashboard, locate the spill incident you just created.
- Click the **"Mark Resolved"** button.
- *What happens:* The backend updates the database. It then looks up the specific WebSocket connection of the fan who reported it.
- *Look at the Fan Window:* The fan instantly receives a chat message: *"✅ Update on your report: The incident has been marked as RESOLVED."* 

### 🧪 Step 6: Global Egress & Mass Coordination (Admin Window -> Fan Window)
- In the Admin Dashboard, click the **"EMERGENCY EVACUATE"** button (or trigger an Egress route).
- *What happens:* The backend calculates the safest exit route for every single fan based on their current section.
- *Look at the Fan Window:* The chat is interrupted by a high-priority push notification, and the map automatically draws a route to the safest exit gate.

---

## 🏗️ TECHNICAL ARCHITECTURE & SYSTEM DESIGN

Stadium Sync is built on a highly decoupled, async-first architecture designed to handle tens of thousands of concurrent connections.

```text
       ┌───────────────┐           ┌──────────────────┐
       │   FAN APP     │           │ ADMIN DASHBOARD  │
       │ (Vercel/Vite) │           │  (Vercel/Vite)   │
       └───────┬───────┘           └────────┬─────────┘
               │                            │
               │ HTTP / WebSockets          │ HTTP / WebSockets
               ▼                            ▼
       ┌──────────────────────────────────────────────┐
       │             FASTAPI BACKEND (Render)         │
       │                                              │
       │  ┌──────────────┐          ┌──────────────┐  │
       │  │ Auth & JWT   │          │  WebSockets  │  │
       │  └──────────────┘          └──────────────┘  │
       │                                              │
       │  ┌────────────────────────────────────────┐  │
       │  │        AI ORCHESTRATION LAYER          │  │
       │  │  (Incident Triage, Map Routing, Chat)  │  │
       │  └───────┬─────────────────────────┬──────┘  │
       └──────────┼─────────────────────────┼─────────┘
                  │                         │
            ┌─────▼─────┐             ┌─────▼─────┐
            │ SQLITE DB │             │ LLM APIS  │
            │(Persistent)             │(Gemini/NIM)
            └───────────┘             └───────────┘
```

### The Stack
- **Frontend:** React 18, Vite, TailwindCSS, Framer Motion, Lucide Icons, Axios.
- **Backend:** FastAPI (Python 3.12), Uvicorn, SQLAlchemy 2.0 (Async), python-jose (JWT), passlib.
- **Database:** SQLite (with WAL mode enabled) / PostgreSQL-ready via asyncpg.
- **AI Models:** Google Gemini 1.5 Flash (Vision + Complex Routing), Nvidia NIM Llama 3.1 70B (Fast NLP Triage).

### Why Async FastAPI?
Handling 80,000 fans requires non-blocking I/O. FastAPI combined with async database drivers ensures that while the backend is waiting for an AI response from Google or Nvidia (which can take 500ms - 2000ms), the main thread is released to handle thousands of other incoming WebSocket heartbeats and requests.

### The Real-Time WebSocket Engine
The backend maintains a custom `ConnectionManager` (`backend/app/api/v1/websocket.py`).
- **Fan Connections:** Stored in memory, mapped by `ticket_id` and `section_id`.
- **Targeted Broadcasting:** When an incident happens in Section N1, the backend doesn't blast 80,000 users. It iterates through the `section_subscribers` mapping and pushes the alert *only* to fans sitting in N1, saving massive bandwidth.

---

## 📁 PROJECT STRUCTURE

Stadium Sync is organized as a monorepo containing both the React frontend and the FastAPI backend.

```text
Stadium_Sync/
├── backend/                   # Python FastAPI Backend
│   ├── app/
│   │   ├── api/v1/            # API routes (chat, admin, websockets, auth)
│   │   ├── core/              # Security, settings, and rate limiting
│   │   ├── models/            # SQLAlchemy ORM schemas (User, Ticket, Incident)
│   │   └── services/          # Business logic, AI orchestration, incident management
│   ├── check_db2.py           # Database verification & seeding script
│   ├── Dockerfile             # Container definition for Render deployment
│   ├── requirements.txt       # Python dependencies (openai, google-genai, fastapi)
│   └── .env.example           # Environment variable template
├── frontend/                  # React & Vite Frontend
│   ├── src/
│   │   ├── components/        # Reusable UI (StadiumChat, StadiumMap, QRScanner)
│   │   ├── pages/             # Main views (AdminDashboard, FanView)
│   │   ├── hooks/             # Custom WebSockets React hooks (useRealtime)
│   │   └── lib/               # Utility functions and API clients
│   ├── index.html             # Entry point
│   ├── vite.config.ts         # Vite configuration
│   └── package.json           # Node dependencies
└── README.md
```

---

## 💻 LOCAL DEVELOPMENT SETUP

To run Stadium Sync locally, you will need Node.js and Python 3.12+.

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/Stadium_Sync.git
cd Stadium_Sync
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (On Windows use `venv\Scripts\activate`)
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`:
```ini
# backend/.env
GEMINI_API_KEY=your_google_ai_key
NVIDIA_NIM_API_KEY=your_nvidia_api_key
SECRET_KEY=generate_a_secure_random_string_here
```

Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```
*(The Swagger UI will be available at `http://localhost:8000/docs`)*

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
```

Create a `.env` file for the frontend:
```ini
# frontend/.env
VITE_API_URL=http://localhost:8000
```

Run the Vite development server:
```bash
npm run dev
```
*(The Fan App will be available at `http://localhost:5173`)*

---

## 🗄️ DATABASE SCHEMA & ERD

The system is built on a robust relational database, accessed asynchronously via SQLAlchemy.

### `users` Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary Key |
| role | Enum | FAN, ADMIN, VOLUNTEER |
| created_at | Timestamp | Account creation |

### `tickets` Table
| Column | Type | Description |
|--------|------|-------------|
| id | String | e.g., 'ticket-001' |
| holder_name | String | Fan name |
| match_id | String | e.g., 'M2026-QF1' |
| checksum | String | Cryptographic anti-spoofing hash |
| seat_id | UUID | Foreign Key to seats |

### `incidents` Table
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary Key |
| ticket_id | String | Who reported it |
| severity | Enum | LOW, MEDIUM, HIGH, CRITICAL |
| category | String | medical, hazard, security, maintenance |
| status | Enum | OPEN, ASSIGNED, RESOLVED |
| ai_triage_result| JSON | Full LLM reasoning payload stored for auditing |

---

## 🔌 API REFERENCE DOCUMENTATION

### Authentication
`POST /api/v1/auth/scan-ticket`
Validates physical QR codes and issues JWTs.
- **Payload:** `{"ticket_id": "string", "match_id": "string", "checksum": "string"}`
- **Response:** `200 OK` with `{"access_token": "eyJ...", "token_type": "bearer"}`

### AI Chat Orchestration
`POST /api/v1/chat/message`
The core agentic endpoint for fans. Internally routes to Gemini.
- **Payload:** `{"message": "string", "image_base64": "string?", "history": [{"role":"user", "content":"hello"}]}`
- **Response:** 
```json
{
  "message": "I'll highlight your seat on the map! 🎯",
  "ui_action": "SHOW_MAP",
  "payload": {
     "target": "seat"
  }
}
```

### Admin Operations
`GET /api/v1/admin/state`
Returns the entire stadium snapshot for the dashboard.
- **Response:** Includes `crowd_map` (live density), `incidents` (active queue), `active_promos`, `volunteers`.

`PATCH /api/v1/admin/incidents/{incident_id}/status`
Updates incident status and triggers WebSocket fan confirmation.

---

## 🔐 SECURITY & AUTHENTICATION

1. **Cryptographic Anti-Spoofing:** QR codes contain a cryptographic checksum. If a fan tries to guess a `ticket_id`, the `/scan-ticket` endpoint rejects it, preventing brute-force seat stealing.
2. **Stateless JWTs:** The entire fan session is encoded in an HMAC-SHA256 JWT. This means the backend doesn't need to perform a database lookup on every chat message just to know where the fan is sitting.
3. **CORS:** Strictly configured in `backend/app/core/config.py` to allow Vercel origins while blocking malicious cross-site requests.
4. **WebSocket Validation:** The `ws://` endpoint requires the JWT token in the query parameters. Invalid tokens immediately drop the TCP connection.

---

## 🚀 FUTURE ROADMAP

If we had more time for the Hackathon, we would implement:
1. **IoT Integration:** Real hardware turnstiles sending MQTT messages to update the `crowd_map` in real-time, replacing our simulated crowd service.
2. **Computer Vision Crowd Counting:** Processing CCTV feeds through YOLOv8 to automatically detect crowd crushes without waiting for ticket scans.
3. **Multi-Language Audio (TTS/STT):** Real-time speech-to-text translation so fans can speak into their phones in any language (e.g. Spanish, French, Japanese) and the AI responds via Text-To-Speech in their native tongue.
4. **Volunteer Mobile App:** A dedicated React Native app for volunteers to receive push notifications, GPS routing to incident locations, and task acceptance buttons.

---

## 🏆 CONCLUSION

Stadium Sync proves that with modern Generative AI, WebSockets, and a decoupled architecture, we can move past static dashboards and reactive security. We can build stadiums that *think*.

Thank you to the Hack2Skill judges! 
Enjoy the demo!
