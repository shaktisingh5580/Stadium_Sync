I'll generate the top comment block for EVERY file in the repository. These are ready to copy-paste directly into each file.

---

# 📝 **HEADER COMMENTS FOR ALL 79 FILES**

## 🔧 **BACKEND FILES (52 Python Files)**

### **Core Application**

#### 1. `backend/app/__init__.py`
```python
"""
===============================================================================
File: backend/app/__init__.py
Purpose: Package initialization and centralized exports for the Stadium Sync 
         application module.
Architecture: Entry point for importing core components throughout the codebase.
             Centralizes public API to reduce circular imports and improve code 
             organization.
Inputs: None (initialization file)
Outputs: Exports settings singleton, database base model, and critical utilities
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 2. `backend/app/main.py`
```python
"""
===============================================================================
File: backend/app/main.py
Purpose: FastAPI application factory - creates and configures the entire 
         backend API with middleware, routes, and lifecycle management.
Architecture: Central orchestrator that initializes all infrastructure 
             (database, Redis, rate limiter, exception handlers) and registers 
             all route routers with versioning. Manages startup/shutdown lifecycle.
Inputs: None (FastAPI entry point via uvicorn app.main:app)
Outputs: Fully configured FastAPI application instance with all middleware, 
         routes, exception handlers, and lifecycle hooks enabled.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

---

### **Core Infrastructure**

#### 3. `backend/app/core/__init__.py`
```python
"""
===============================================================================
File: backend/app/core/__init__.py
Purpose: Package initialization for core infrastructure modules (config, 
         database, security, audit logging).
Architecture: Centralizes exports from core modules to enable clean imports 
             like 'from app.core import get_settings, get_db'.
Inputs: None (package initialization)
Outputs: Centralized access to config, database, security, and audit utilities
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 4. `backend/app/core/audit_logger.py`
```python
"""
===============================================================================
File: backend/app/core/audit_logger.py
Purpose: Compliance and security audit trail - immutably logs all sensitive 
         operations (ticket scans, token issuance, incidents, admin actions) 
         for investigation and regulatory compliance.
Architecture: Async audit logging with PostgreSQL persistence. Each log entry 
             is immutable (no updates, only inserts) with timestamp, actor ID, 
             resource ID, outcome, and rich context (IP, details JSON).
Inputs: Audit events from various services (auth, incidents, admin, etc.) with 
        action type, actor, resource, details, and status.
Outputs: Immutable audit_logs table records for compliance, forensics, and 
         real-time security monitoring (e.g., detect abuse patterns).
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

#### 5. `backend/app/core/config.py`
```python
"""
===============================================================================
File: backend/app/core/config.py
Purpose: Centralized configuration management using Pydantic Settings - loads 
         environment variables, validates types, enforces production security 
         policies, and provides singleton access.
Architecture: Pydantic BaseSettings model with field validators for production 
             safety. Refuses to start if DEBUG=true in prod, SECRET_KEY < 32 
             chars, CORS wildcard in prod, or mock AI fallback enabled in prod.
Inputs: Environment variables from .env file or container secrets 
        (APP_ENV, DEBUG, DATABASE_URL, REDIS_URL, GEMINI_API_KEY_1, etc.)
Outputs: Settings singleton (get_settings()) with validated, type-safe 
         configuration for entire application.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 6. `backend/app/core/database.py`
```python
"""
===============================================================================
File: backend/app/core/database.py
Purpose: Async SQLAlchemy engine and session management - configures connection 
         pool optimized for deployment target (SQLite for local, PostgreSQL 
         with QueuePool for staging, Neon Serverless with NullPool for prod).
Architecture: Creates AsyncSession factory with automatic transaction management 
             (auto-commit on success, auto-rollback on error). Connection pool 
             strategy varies by database type: NullPool for serverless, QueuePool 
             for persistent database.
Inputs: DATABASE_URL from config, connection pool settings 
        (pool_size, max_overflow, pool_recycle).
Outputs: get_db() dependency for routes (provides AsyncSession), 
         engine.connect() for admin scripts, health check function.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 7. `backend/app/core/exceptions.py`
```python
"""
===============================================================================
File: backend/app/core/exceptions.py
Purpose: Custom HTTP exception hierarchy - maps Python exceptions to proper 
         HTTP status codes and sanitizes error responses (no stack traces 
         to clients, server-side logging only).
Architecture: Exception classes inherit from FastAPI HTTPException. Each has 
             specific status code (400, 401, 403, 404, 409, 429, 500) and 
             message template. Central exception handler registered in main.py 
             logs all errors server-side with request_id for debugging.
Inputs: Exceptions raised throughout business logic and route handlers.
Outputs: Sanitized JSON error responses to clients, full error logs server-side.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

#### 8. `backend/app/core/rate_limiter.py`
```python
"""
===============================================================================
File: backend/app/core/rate_limiter.py
Purpose: Request rate limiting via SlowAPI - prevents DDoS, brute-force 
         attacks, and fair-queues API access. Per-endpoint and per-user 
         limits (auth: 10/min, AI: 20/min, IoT: 300/min).
Architecture: SlowAPI uses Redis backend (or in-memory fallback) to track 
             request counts with TTL windows. Decorators like 
             @limiter.limit("10/minute") applied to route handlers.
Inputs: Limiter configuration from settings (rate limits per endpoint).
Outputs: 429 Too Many Requests response when limit exceeded.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

#### 9. `backend/app/core/redis_client.py`
```python
"""
===============================================================================
File: backend/app/core/redis_client.py
Purpose: Redis connection pool with graceful in-memory fallback - caches 
         frequently accessed data (stadium layout, crowd predictions), stores 
         session state, rate limit counters, and token revocation list.
Architecture: Redis async client with connection pooling. If Redis unavailable, 
             falls back to in-memory dict for development/testing. Supports 
             key expiration (TTL) for automatic cleanup.
Inputs: REDIS_URL from config, optional REDIS_ENABLED flag.
Outputs: Cached data lookups (< 1ms latency), rate limit counters, token 
         revocation tracking, session management.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 10. `backend/app/core/security.py`
```python
"""
===============================================================================
File: backend/app/core/security.py
Purpose: JWT token management - creation, verification, expiration checks, 
         and revocation via JTI (JWT ID) tracking in Redis.
Architecture: HMAC-SHA256 signing with configurable expiry (fan: 4h, 
             volunteer: 12h, admin: 8h). Tokens include claims: sub (ticket_id), 
             role, aud (audience for role isolation), jti (unique ID for 
             revocation), iat (issued at), exp (expiration).
Inputs: Credential data (ticket_id, name, role), optional custom expiry.
Outputs: Encoded JWT string, decoded/verified payload, revocation capability.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

---

### **Middleware**

#### 11. `backend/app/middleware/__init__.py`
```python
"""
===============================================================================
File: backend/app/middleware/__init__.py
Purpose: Package initialization for middleware modules (logging, security 
         headers, request ID injection).
Architecture: Centralizes middleware exports for clean imports.
Inputs: None (package initialization)
Outputs: Middleware classes available as 'from app.middleware import ...'
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 12. `backend/app/middleware/logging_mw.py`
```python
"""
===============================================================================
File: backend/app/middleware/logging_mw.py
Purpose: Structured request/response logging - logs all API calls with method, 
         path, status, duration, response size. Sanitizes sensitive headers 
         (Authorization, API keys) before logging.
Architecture: BaseHTTPMiddleware that wraps all requests. Logs method, path, 
             status code, duration (ms), response size. Stores timing in 
             response headers for observability.
Inputs: All HTTP requests passing through the application.
Outputs: Structured log entries for operational visibility and debugging.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 13. `backend/app/middleware/request_id.py`
```python
"""
===============================================================================
File: backend/app/middleware/request_id.py
Purpose: X-Request-ID injection - assigns unique UUID to every request for 
         end-to-end tracing through logs, database, and external APIs.
Architecture: Middleware generates UUID (if not present in header) and stores 
             in request.state.request_id. All downstream operations can access 
             and log this ID for correlation.
Inputs: HTTP requests (with optional existing X-Request-ID header).
Outputs: UUID stored in request state and included in X-Request-ID response 
         header for client-side bug reporting.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 14. `backend/app/middleware/security_headers.py`
```python
"""
===============================================================================
File: backend/app/middleware/security_headers.py
Purpose: HTTP security header injection - adds CSP, X-Frame-Options, HSTS, 
         X-Content-Type-Options to prevent XSS, clickjacking, and MIME sniffing.
Architecture: Middleware appends security headers to all responses. Headers 
             configured per OWASP recommendations.
Inputs: All HTTP responses.
Outputs: Responses with security headers added for browser-level protection.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

---

### **Models (SQLAlchemy ORM)**

#### 15. `backend/app/models/__init__.py`
```python
"""
===============================================================================
File: backend/app/models/__init__.py
Purpose: Package initialization for SQLAlchemy ORM models - centralizes model 
         exports and Base class for easy importing throughout codebase.
Architecture: Exports Base class (declarative base) and all model classes 
             (Ticket, Section, Incident, Crowd, Volunteer, etc.) to avoid 
             circular imports.
Inputs: None (package initialization)
Outputs: Centralized access to ORM models and Base for schema definition.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 16. `backend/app/models/base.py`
```python
"""
===============================================================================
File: backend/app/models/base.py
Purpose: SQLAlchemy Declarative Base - parent class for all ORM models with 
         common columns (id, created_at, updated_at) and table configuration.
Architecture: Provides Base class that all models inherit from. Automatically 
             adds UUID primary key, created_at timestamp (UTC), updated_at 
             timestamp (UTC) to every table.
Inputs: None (base class definition)
Outputs: Base class for model definition, automatic audit timestamps on all 
         entities.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 17. `backend/app/models/crowd.py`
```python
"""
===============================================================================
File: backend/app/models/crowd.py
Purpose: Crowd density and IoT data models - tracks real-time crowd counts 
         per section, predicts density 15 minutes ahead using linear regression, 
         and broadcasts congestion alerts.
Architecture: Three main tables: CrowdDensity (current snapshot), 
             CrowdPrediction (ML forecast), CrowdAlert (broadcast message). 
             Data updated every 30s from IoT sensors.
Inputs: IoT turnstile counts (POST /crowd/ingest), historical density data.
Outputs: Real-time heatmap for frontend, crowdPrediction alerts, WebSocket 
         broadcasts to fans in congested sections.
Hackathon Vertical: Crowd Management & Real-Time Decision Support
===============================================================================
"""
```

#### 18. `backend/app/models/incident.py`
```python
"""
===============================================================================
File: backend/app/models/incident.py
Purpose: Incident tracking and AI triage - models incident reports (medical, 
         security, facilities) with Gemini AI categorization, severity 
         classification, and resolution tracking.
Architecture: Incident table with status workflow (reported → triaged → 
             dispatched → resolved). IncidentUpdate tracks escalation history. 
             Links to Gemini triage result (severity, category, action).
Inputs: Fan/volunteer incident reports with description.
Outputs: Incident records with AI-determined severity, category, and dispatch 
         action for volunteer assignment.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 19. `backend/app/models/stadium.py`
```python
"""
===============================================================================
File: backend/app/models/stadium.py
Purpose: Stadium layout and infrastructure models - defines stadium geometry 
         (sections, gates, amenities) with SVG coordinates for digital twin 
         rendering and routing algorithms.
Architecture: Stadium (match venue), Section (seating), Gate (entry/exit), 
             Amenity (POIs like restrooms, food, medical). All have SVG 
             coordinates (x, y) for precise map rendering.
Inputs: Stadium configuration (loaded at match start from database).
Outputs: Geometry data for routing algorithms, POI locations, accessible 
         amenities, digital twin visualization.
Hackathon Vertical: Navigation & Accessibility
===============================================================================
"""
```

#### 20. `backend/app/models/ticket.py`
```python
"""
===============================================================================
File: backend/app/models/ticket.py
Purpose: Ticket and seating models - defines ticket ownership, seat 
         assignment, accessibility needs, and transit preferences.
Architecture: Ticket (QR code, holder info, validity status), Seat (section, 
             row, number, SVG coords), Section (seating area). Ticket links 
             to Seat, Seat links to Section.
Inputs: Ticket data from QR code, seating assignments.
Outputs: Fan session context (ticket, seat, accessibility, transit), used 
         throughout app for personalization.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

#### 21. `backend/app/models/volunteer.py`
```python
"""
===============================================================================
File: backend/app/models/volunteer.py
Purpose: Volunteer and dispatch tracking - models staff members with 
         geolocation, real-time position updates, and incident assignments.
Architecture: Volunteer (staff info), VolunteerLocation (GPS + timestamp), 
             Dispatch (incident assignment + ETA). VolunteerLocation updated 
             every 10s via mobile app.
Inputs: Volunteer GPS coordinates, incident assignments.
Outputs: Volunteer positions for dispatch routing, ETA calculations, admin 
         visibility, crowd management deployment.
Hackathon Vertical: Real-Time Decision Support & Crowd Management
===============================================================================
"""
```

---

### **Schemas (Pydantic Validation)**

#### 22. `backend/app/schemas/__init__.py`
```python
"""
===============================================================================
File: backend/app/schemas/__init__.py
Purpose: Package initialization for Pydantic request/response schemas - 
         centralizes validation and serialization models.
Architecture: Exports all schema classes to enable clean imports like 
             'from app.schemas import QRScanRequest, ChatResponse'.
Inputs: None (package initialization)
Outputs: Centralized schema access for route handlers and documentation.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 23. `backend/app/schemas/auth.py`
```python
"""
===============================================================================
File: backend/app/schemas/auth.py
Purpose: Authentication request/response schemas - validates QR scan input, 
         JWT token format, and fan session deserialization.
Architecture: Pydantic models for QRScanRequest, QRScanResponse, 
             TokenRefreshResponse, FanSession with type validation and 
             field constraints (max_length, regex, etc.).
Inputs: QR payload (JSON string with ticket_id, match_id, checksum).
Outputs: Validated FanSession with ticket, seat, accessibility, transit data 
         for JWT payload and API responses.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

#### 24. `backend/app/schemas/chat.py`
```python
"""
===============================================================================
File: backend/app/schemas/chat.py
Purpose: Chat API schemas - validates fan queries and structures AI responses 
         with UI action commands (show route, show POI, etc.).
Architecture: ChatRequest (query + context), ChatResponse (text + UI action). 
             Constrains query length (< 500 chars) and UI actions to specific 
             enum values.
Inputs: Fan natural language query with context (seat, accessibility, etc.).
Outputs: AI response with structured UI action for frontend to render.
Hackathon Vertical: Navigation & Multilingual Assistance
===============================================================================
"""
```

#### 25. `backend/app/schemas/crowd.py`
```python
"""
===============================================================================
File: backend/app/schemas/crowd.py
Purpose: Crowd data schemas - validates IoT sensor input and structures 
         real-time heatmap/prediction responses.
Architecture: CrowdIngestRequest (section, count, timestamp), 
             CrowdDensityResponse (current per-section), CrowdPredictionResponse 
             (15-min forecast per section).
Inputs: IoT turnstile counts from sensors.
Outputs: Real-time density heatmap and predictions for frontend display.
Hackathon Vertical: Crowd Management & Real-Time Decision Support
===============================================================================
"""
```

#### 26. `backend/app/schemas/eco_vision.py`
```python
"""
===============================================================================
File: backend/app/schemas/eco_vision.py
Purpose: Eco-Vision AI schemas - validates waste camera image input and 
         structures Gemini Vision classification response.
Architecture: WasteClassificationRequest (base64 image), 
             WasteClassificationResponse (waste_type, bin_color, confidence, 
             eco_fact).
Inputs: Base64-encoded camera image from fan.
Outputs: AI-classified waste type, bin color, and nearest bin routing.
Hackathon Vertical: Sustainability
===============================================================================
"""
```

#### 27. `backend/app/schemas/incident.py`
```python
"""
===============================================================================
File: backend/app/schemas/incident.py
Purpose: Incident schemas - validates incident reports and structures AI 
         triage responses with severity/category/action.
Architecture: IncidentReportRequest (description), IncidentTriageResponse 
             (severity enum, category enum, recommended_actions).
Inputs: Fan/volunteer incident description.
Outputs: AI-determined severity level and category for automation + dispatch.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 28. `backend/app/schemas/navigation.py`
```python
"""
===============================================================================
File: backend/app/schemas/navigation.py
Purpose: Navigation schemas - validates transit preferences and structures 
         computed exit route responses.
Architecture: TransitPreferenceRequest (enum: metro/bus/rideshare/parking), 
             RouteResponse (path coordinates, duration, accessibility_safe).
Inputs: Fan's transit preference selection.
Outputs: Computed route to nearest transit station of chosen type.
Hackathon Vertical: Navigation & Transportation
===============================================================================
"""
```

#### 29. `backend/app/schemas/volunteer.py`
```python
"""
===============================================================================
File: backend/app/schemas/volunteer.py
Purpose: Volunteer schemas - validates location updates and structures 
         dispatch/assignment responses.
Architecture: VolunteerLocationUpdate (lat, lon, timestamp), DispatchRequest 
             (incident_id, volunteer_id), VolunteerResponse (volunteer info 
             for admin dashboard).
Inputs: GPS coordinates from volunteer mobile app.
Outputs: Volunteer position for dispatch routing and admin visibility.
Hackathon Vertical: Real-Time Decision Support & Crowd Management
===============================================================================
"""
```

---

### **Services (Business Logic)**

#### 30. `backend/app/services/__init__.py`
```python
"""
===============================================================================
File: backend/app/services/__init__.py
Purpose: Package initialization for business logic services - centralizes 
         service exports for easy importing.
Architecture: Exports all service classes/functions to enable clean imports 
             like 'from app.services import chat_service, incident_service'.
Inputs: None (package initialization)
Outputs: Centralized service access throughout application.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 31. `backend/app/services/crowd_service.py`
```python
"""
===============================================================================
File: backend/app/services/crowd_service.py
Purpose: Crowd analytics engine - ingests IoT turnstile data, computes 
         real-time density, predicts 15-min future congestion via linear 
         regression, triggers congestion alerts.
Architecture: Ingest flow: IoT count → aggregate by section → compute density % 
             → compare against thresholds → broadcast alerts. Prediction flow: 
             historical data → linear regression model → 15-min forecast.
Inputs: Turnstile counts from IoT sensors (POST /crowd/ingest).
Outputs: Real-time density heatmap, 15-min predictions, WebSocket alerts to 
         fans in congested sections.
Hackathon Vertical: Crowd Management & Real-Time Decision Support
===============================================================================
"""
```

#### 32. `backend/app/services/dispatch_service.py`
```python
"""
===============================================================================
File: backend/app/services/dispatch_service.py
Purpose: Volunteer dispatch and routing - finds nearest available volunteer 
         to incident, computes ETA, sends dispatch notification, tracks 
         assignment status.
Architecture: Query active volunteers → calculate distance to incident → sort 
             by proximity → send dispatch to nearest → track status 
             (dispatched → arrived → resolved). Uses SVG coordinate distance.
Inputs: Incident location (svg_x, svg_y), active volunteer positions.
Outputs: Dispatch assignment, push notification to volunteer, ETA estimate, 
         assignment tracking.
Hackathon Vertical: Real-Time Decision Support & Crowd Management
===============================================================================
"""
```

#### 33. `backend/app/services/egress_service.py`
```python
"""
===============================================================================
File: backend/app/services/egress_service.py
Purpose: Evacuation and exit route computation - computes personalized exit 
         paths for each fan, respects accessibility constraints, balances 
         load across gates, triggered by emergency or anomaly detection.
Architecture: For each fan: get seat → find nearest gate (Dijkstra) → if 
             wheelchair: filter stairs/escalators → compute ETA → add route 
             to response queue. Load-balance: cap fans per gate.
Inputs: Connected fan list with seats, accessibility flags; emergency trigger.
Outputs: Personalized routes to nearest appropriate gate, ETA countdowns, 
         WebSocket broadcasts.
Hackathon Vertical: Real-Time Decision Support & Accessibility
===============================================================================
"""
```

#### 34. `backend/app/services/gemini_client.py`
```python
"""
===============================================================================
File: backend/app/services/gemini_client.py
Purpose: Google Gemini 2.5 Flash integration - the AI brain executing 6 
         distinct use cases: Fan concierge, incident triage, eco-vision waste 
         classification, admin copilot, multilingual detection, CV anomaly 
         analysis.
Architecture: Implements async Gemini API calls with structured output schemas 
             (JSON responses validated). System prompts hardcoded (never user 
             input). Request/response sanitization. Key rotation support.
Inputs: Queries (fan chat, incident description, images for vision), stadium 
        context, operational state for admin copilot.
Outputs: AI-generated responses (text, classification, triage result, 
         recommendations) in validated JSON format.
Hackathon Vertical: Operational Intelligence, Navigation, Multilingual 
                    Assistance, Sustainability, Real-Time Decision Support
===============================================================================
"""
```

#### 35. `backend/app/services/incident_service.py`
```python
"""
===============================================================================
File: backend/app/services/incident_service.py
Purpose: Incident lifecycle management - accepts incident reports, sends to 
         Gemini for AI triage, creates incident record, dispatches nearest 
         volunteer, tracks resolution status.
Architecture: Report flow: receive description → AI triage (severity, 
             category, action) → create DB record → dispatch volunteer → 
             broadcast alert. Resolution: update status → log completion.
Inputs: Incident description from fan/volunteer.
Outputs: Incident record with AI triage, volunteer dispatch, real-time alert 
         broadcast.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 36. `backend/app/services/navigation_service.py`
```python
"""
===============================================================================
File: backend/app/services/navigation_service.py
Purpose: Indoor navigation and routing - computes shortest paths through 
         stadium via Dijkstra's algorithm, respects accessibility constraints, 
         accounts for transit preference, returns SVG coordinates for rendering.
Architecture: Build graph of stadium sections/gates/amenities → Dijkstra 
             shortest path → filter by accessibility (no stairs if wheelchair) 
             → filter by transit type (metro entrance vs parking) → return 
             coordinate path.
Inputs: Fan seat, destination (amenity/gate/transit), accessibility flag, 
        transit preference.
Outputs: Ordered path coordinates (svg_x, svg_y), duration estimate, POI 
         details.
Hackathon Vertical: Navigation & Accessibility
===============================================================================
"""
```

#### 37. `backend/app/services/ticket_service.py`
```python
"""
===============================================================================
File: backend/app/services/ticket_service.py
Purpose: QR ticket validation and authentication - decodes QR payload, verifies 
         HMAC-SHA256 checksum, validates ticket in database, builds fan session 
         with seat and accessibility info.
Architecture: Decode QR JSON → verify checksum vs SIGNING_KEY → query Ticket 
             table → load relationships (Seat, Section) → build FanSession → 
             return for JWT encoding.
Inputs: QR payload (JSON: ticket_id, match_id, checksum).
Outputs: Validated FanSession with ticket, seat, accessibility, transit data; 
         marks ticket as scanned.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

---

### **API Routes (Endpoints)**

#### 38. `backend/app/api/__init__.py`
```python
"""
===============================================================================
File: backend/app/api/__init__.py
Purpose: Package initialization for API routes - centralizes route router 
         imports.
Architecture: Exports v1_router and future v2_router for main.py inclusion.
Inputs: None (package initialization)
Outputs: Router instances for API route registration.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 39. `backend/app/api/deps.py`
```python
"""
===============================================================================
File: backend/app/api/deps.py
Purpose: Dependency injection utilities - provides reusable FastAPI Depends() 
         functions for database sessions, JWT authentication, admin 
         authorization.
Architecture: get_db() → AsyncSession (auto-commit/rollback), get_current_user() 
             → verified JWT payload, get_admin_user() → admin-only verification.
Inputs: FastAPI Request (headers for JWT extraction), database engine.
Outputs: Injected dependencies: database sessions, authenticated user context, 
         admin verification.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

#### 40. `backend/app/api/v1/__init__.py`
```python
"""
===============================================================================
File: backend/app/api/v1/__init__.py
Purpose: Package initialization for v1 API routes - enables future API 
         versioning (v1 vs v2 without breaking clients).
Architecture: Centralizes v1 route modules.
Inputs: None (package initialization)
Outputs: v1 route modules available for import.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 41. `backend/app/api/v1/admin.py`
```python
"""
===============================================================================
File: backend/app/api/v1/admin.py
Purpose: Admin command center API - provides operational dashboard, AI copilot, 
         emergency evacuation triggers, computer vision webhook intake, flash 
         sale targeting.
Architecture: Protected routes (admin-only). Endpoints: /admin/state (full 
             dashboard), /admin/chat (Gemini with context), /admin/evacuate 
             (broadcast routes), /admin/cv-webhook (edge node analysis).
Inputs: Admin queries, evacuation triggers, CV frames from edge cameras.
Outputs: Operational state (crowd density, incidents, volunteers), AI 
         recommendations, emergency broadcasts.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 42. `backend/app/api/v1/auth.py`
```python
"""
===============================================================================
File: backend/app/api/v1/auth.py
Purpose: Authentication endpoints - QR scan to JWT issuance, session retrieval, 
         token refresh for long-duration matches.
Architecture: POST /scan-ticket (QR validation → JWT), GET /me (session info), 
             POST /refresh (extend expiry). All responses include fan context 
             (seat, accessibility, transit).
Inputs: QR payload, optional token refresh.
Outputs: JWT tokens with fan session, user info, expiration times.
Hackathon Vertical: Security & Authentication
===============================================================================
"""
```

#### 43. `backend/app/api/v1/chat.py`
```python
"""
===============================================================================
File: backend/app/api/v1/chat.py
Purpose: Fan AI concierge endpoint - natural language queries answered by 
         Gemini with stadium context (navigation, amenities, rules, 
         accessibility, transit).
Architecture: POST /chat accepts query + fan context → enriches with stadium 
             data → sends to Gemini → returns response + UI action (SHOW_ROUTE, 
             SHOW_POI, etc.).
Inputs: Fan query (natural language), fan session context.
Outputs: AI response with navigation directions, POI info, UI action command.
Hackathon Vertical: Navigation, Multilingual Assistance, Accessibility
===============================================================================
"""
```

#### 44. `backend/app/api/v1/crowd.py`
```python
"""
===============================================================================
File: backend/app/api/v1/crowd.py
Purpose: Crowd data ingestion and broadcasting - IoT sensors post turnstile 
         counts, frontend fetches real-time heatmap, WebSocket broadcasts 
         congestion alerts.
Architecture: POST /crowd/ingest (IoT), GET /crowd/map/{match_id} (heatmap), 
             WebSocket broadcast on density threshold exceeded.
Inputs: IoT turnstile counts, match ID for heatmap query.
Outputs: Real-time density heatmap, WebSocket alerts, predictions.
Hackathon Vertical: Crowd Management & Real-Time Decision Support
===============================================================================
"""
```

#### 45. `backend/app/api/v1/eco_vision.py`
```python
"""
===============================================================================
File: backend/app/api/v1/eco_vision.py
Purpose: Sustainability: waste classification API - camera image → Gemini 
         Vision classifies waste type → routes to nearest bin with eco facts.
Architecture: POST /eco-vision/classify (base64 image) → Gemini Vision → 
             returns waste classification + bin routing.
Inputs: Base64-encoded waste image.
Outputs: Waste type, bin color, nearest bin location, environmental fact.
Hackathon Vertical: Sustainability
===============================================================================
"""
```

#### 46. `backend/app/api/v1/egress.py`
```python
"""
===============================================================================
File: backend/app/api/v1/egress.py
Purpose: Exit route computation and evacuation - computes personalized routes, 
         respects accessibility, broadcasts emergency evacuation.
Architecture: GET /egress/route (compute route to nearest gate), POST 
             /egress/trigger (staff-initiated evacuation).
Inputs: Fan seat, accessibility flag, evacuation trigger.
Outputs: Exit route with ETA, evacuation broadcasts via WebSocket.
Hackathon Vertical: Real-Time Decision Support & Accessibility
===============================================================================
"""
```

#### 47. `backend/app/api/v1/health.py`
```python
"""
===============================================================================
File: backend/app/api/v1/health.py
Purpose: Health check endpoint - signals service status to Render load 
         balancer. Checks database, Redis, and Gemini API availability.
Architecture: GET /health → returns 200 OK if all critical dependencies 
             available, 503 Service Unavailable if any down.
Inputs: None (periodic health checks from load balancer).
Outputs: Health status JSON with dependency states.
Hackathon Vertical: Operational Intelligence
===============================================================================
"""
```

#### 48. `backend/app/api/v1/incidents.py`
```python
"""
===============================================================================
File: backend/app/api/v1/incidents.py
Purpose: Incident reporting API - fans/volunteers report problems, Gemini AI 
         triages (severity, category, action), dispatches volunteer, broadcasts 
         alert.
Architecture: POST /incidents (report) → Gemini triage → create DB record → 
             dispatch → broadcast.
Inputs: Incident description, category hint.
Outputs: Incident record with AI triage, dispatch action, alert broadcast.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 49. `backend/app/api/v1/navigation.py`
```python
"""
===============================================================================
File: backend/app/api/v1/navigation.py
Purpose: Navigation API - fan sets transit preference, routes to nearest 
         station/exit of chosen type (metro/bus/rideshare/parking).
Architecture: POST /navigation/transit (set preference) → GET /navigation/route 
             (compute route to matching transit).
Inputs: Transit preference (enum), fan seat.
Outputs: Route to transit station, accessibility safe path.
Hackathon Vertical: Navigation & Transportation
===============================================================================
"""
```

#### 50. `backend/app/api/v1/router.py`
```python
"""
===============================================================================
File: backend/app/api/v1/router.py
Purpose: V1 API router aggregator - includes all v1 endpoint modules 
         (health, auth, chat, incidents, crowd, admin, etc.) with prefixes 
         and tags for Swagger docs.
Architecture: Creates APIRouter, includes all v1 routes with /api/v1 prefix.
Inputs: None (route registration aggregation)
Outputs: Combined v1_router for main.py inclusion.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
```

#### 51. `backend/app/api/v1/volunteers.py`
```python
"""
===============================================================================
File: backend/app/api/v1/volunteers.py
Purpose: Volunteer management API - track real-time positions, dispatch to 
         incidents, admin visibility.
Architecture: POST /volunteers/location (GPS update), GET /volunteers/active 
             (admin dashboard), POST /volunteers/dispatch (assignment).
Inputs: GPS coordinates from volunteer app, incident assignments.
Outputs: Volunteer positions, dispatch notifications, assignment tracking.
Hackathon Vertical: Real-Time Decision Support & Crowd Management
===============================================================================
"""
```

#### 52. `backend/app/api/v1/websocket.py`
```python
"""
===============================================================================
File: backend/app/api/v1/websocket.py
Purpose: WebSocket manager - persistent bidirectional connections for 
         real-time alerts (evacuation, crowd, incidents). Replaces polling 
         for instant delivery (< 500ms latency).
Architecture: WS /api/v1/ws?token=jwt → validate JWT → add to connection pool 
             → subscribe to events → broadcast messages → auto-reconnect on 
             failure.
Inputs: JWT token for authentication, real-time events (admin broadcasts, 
        crowd alerts, incident updates).
Outputs: Real-time message delivery to connected fans.
Hackathon Vertical: Real-Time Decision Support & Crowd Management
===============================================================================
"""
```

---

## 🎨 **FRONTEND FILES (27 TypeScript/TSX Files)**

### **Core Files**

#### 53. `frontend/src/main.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/main.tsx
 * Purpose: React application bootstrap - mounts React App component to DOM 
 *          (#root) and initializes React Strict Mode for dev-only error 
 *          checking.
 * Architecture: Entry point for Vite dev server and production build. Sets up 
 *               StrictMode wrapper to catch side effects and state mutations.
 * Inputs: React App component, DOM element with id="root".
 * Outputs: React application mounted and rendering.
 * Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
 * ===============================================================================
 */
```

#### 54. `frontend/src/App.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/App.tsx
 * Purpose: Root React component - orchestrates route logic, authentication 
 *          state, WebSocket initialization, theme provider setup.
 * Architecture: Central component tree orchestrator. Manages JWT token 
 *               (sessionStorage), initializes WebSocket, conditional rendering 
 *               based on auth role (fan vs admin).
 * Inputs: JWT token from sessionStorage, route/page context.
 * Outputs: Rendered UI (FanInterface or AdminDashboard) based on auth state.
 * Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
 * ===============================================================================
 */
```

#### 55. `frontend/src/setupTests.ts`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/setupTests.ts
 * Purpose: Vitest/React Testing Library configuration - imports testing 
 *          utilities and sets up global test environment.
 * Architecture: Auto-loaded by Vitest before each test file. Configures DOM 
 *               matchers (toBeInTheDocument, etc.), global mocks.
 * Inputs: None (configuration file).
 * Outputs: Test environment with matchers available globally in all test files.
 * Hackathon Vertical: Code Quality & Testing
 * ===============================================================================
 */
```

### **Styling**

#### 56. `frontend/src/index.css`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/index.css
 * Purpose: Global CSS styles - defines CSS variables (colors, sizes), base 
 *          element styles, utility classes, animations.
 * Architecture: Loaded globally in main.tsx. CSS variables enable theme 
 *               switching. Utilities like .fadeIn, .slideUp for animations.
 * Inputs: None (stylesheet).
 * Outputs: Global styling applied to entire app.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */
```

#### 57. `frontend/src/App.css`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/App.css
 * Purpose: App component-level styles - layout, transitions, responsive design.
 * Architecture: Scoped styles for App component and immediate children.
 * Inputs: None (stylesheet).
 * Outputs: Component-specific styling.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */
```

### **API Client**

#### 58. `frontend/src/api/client.ts`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/api/client.ts
 * Purpose: Axios HTTP client configuration - sets base URL, request/response 
 *          interceptors, JWT token auto-injection, error handling.
 * Architecture: Creates Axios instance with interceptors: request adds 
 *               Authorization header from sessionStorage; response handles 401 
 *               (token expired) by triggering refresh/logout.
 * Inputs: VITE_API_URL environment variable, JWT token from sessionStorage.
 * Outputs: Configured Axios instance for API calls with auto-token management.
 * Hackathon Vertical: Security & Authentication
 * ===============================================================================
 */
```

#### 59. `frontend/src/api/index.ts`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/api/index.ts
 * Purpose: API function wrappers - typed functions for backend endpoints 
 *          (scanTicket, sendChat, getState, etc.).
 * Architecture: Wraps Axios calls with type safety. Each function corresponds 
 *               to backend endpoint, with type-checked params/return values.
 * Inputs: Endpoint-specific parameters (queries, bodies).
 * Outputs: Typed Promise responses matching backend schemas.
 * Hackathon Vertical: Code Quality & Security
 * ===============================================================================
 */
```

#### 60. `frontend/src/api/admin.ts`
```typescript
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
```

### **React Hooks**

#### 61. `frontend/src/hooks/useChat.ts`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/hooks/useChat.ts
 * Purpose: Chat state management hook - maintains message history, sends 
 *          queries to backend, handles loading/error states.
 * Architecture: useChat() hook returns: messages[], loading, error, sendMessage() 
 *               function. Manages optimistic UI updates and error recovery.
 * Inputs: Initial messages, fan context.
 * Outputs: Chat state, methods to add messages and send queries.
 * Hackathon Vertical: Navigation & Real-Time Decision Support
 * ===============================================================================
 */
```

#### 62. `frontend/src/hooks/useRealtime.ts`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/hooks/useRealtime.ts
 * Purpose: WebSocket connection hook - manages persistent bidirectional 
 *          connection, subscribes to real-time events (evacuation, crowd, 
 *          incidents), auto-reconnects on failure.
 * Architecture: useRealtime() hook manages WebSocket lifecycle. Emits events 
 *               via callback; auto-reconnect with exponential backoff on 
 *               connection failure.
 * Inputs: JWT token, event callback function.
 * Outputs: WebSocket connection state, event handler.
 * Hackathon Vertical: Real-Time Decision Support & Crowd Management
 * ===============================================================================
 */
```

### **Types**

#### 63. `frontend/src/types/index.ts`
```typescript
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
```

### **Main Components**

#### 64. `frontend/src/components/StadiumChat.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/StadiumChat.tsx
 * Purpose: Primary fan interface - chat UI + map display orchestration. 
 *          Renders message list, input field, and integrates map component 
 *          to show AI-suggested routes.
 * Architecture: Main component combining useChat hook with StadiumMap 
 *               rendering. Animates messages, shows loading state, displays 
 *               map when navigation suggested.
 * Inputs: Fan session (ticket, seat, accessibility), WebSocket events.
 * Outputs: Chat UI with route visualization.
 * Hackathon Vertical: Navigation & Real-Time Decision Support
 * ===============================================================================
 */
```

### **Auth Components**

#### 65. `frontend/src/components/auth/QRScanner.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/auth/QRScanner.tsx
 * Purpose: QR code scanner component - gate-keeping authentication. Captures 
 *          QR from camera, sends payload to backend, stores JWT on success.
 * Architecture: Integrates @yudiel/react-qr-scanner library. Requests camera 
 *               permission, detects QR payload, validates via backend, stores 
 *               token in sessionStorage, redirects to main app.
 * Inputs: Camera feed (browser permission required).
 * Outputs: JWT token stored in sessionStorage, auth state updated.
 * Hackathon Vertical: Security & Authentication
 * ===============================================================================
 */
```

### **Map Components**

#### 66. `frontend/src/components/map/StadiumMap.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/map/StadiumMap.tsx
 * Purpose: Interactive SVG map - visualizes stadium geometry, real-time crowd 
 *          heatmap, animated route suggestions, clickable POIs.
 * Architecture: SVG canvas (800x800) renders sections, gates, amenities. 
 *               Overlays crowd heatmap with color intensity. Animates fan 
 *               route step-by-step. Clickable POIs show details.
 * Inputs: Stadium layout, crowd density data, route coordinates.
 * Outputs: Interactive map visualization with real-time updates.
 * Hackathon Vertical: Navigation & Crowd Management
 * ===============================================================================
 */
```

#### 67. `frontend/src/components/map/StadiumMap.css`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/map/StadiumMap.css
 * Purpose: Map component styles - animations, hover effects, heatmap gradient.
 * Architecture: CSS animations for route rendering, hover effects for POI 
 *               interactivity, gradient for crowd density color mapping.
 * Inputs: None (stylesheet).
 * Outputs: Styled map with animations and visual feedback.
 * Hackathon Vertical: Navigation & Code Quality
 * ===============================================================================
 */
```

### **UI Components**

#### 68. `frontend/src/components/ui/animated-ai-chat.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/ui/animated-ai-chat.tsx
 * Purpose: Animated chat bubble component - renders AI response with 
 *          typewriter effect, ARIA live region for screen readers, copy 
 *          button, syntax highlighting.
 * Architecture: Streams response text character-by-character with animation. 
 *               aria-live="polite" announces to screen readers. Supports 
 *               emoji, code blocks, markdown-like formatting.
 * Inputs: AI response text, is_streaming flag.
 * Outputs: Animated chat bubble with accessible markup.
 * Hackathon Vertical: Accessibility & Multilingual Assistance
 * ===============================================================================
 */
```

#### 69. `frontend/src/components/ui/message-bubble.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/ui/message-bubble.tsx
 * Purpose: Reusable message bubble component - renders fan or AI message 
 *          with appropriate styling (left/right alignment), timestamp, role.
 * Architecture: Takes message object with content, sender (fan/AI), timestamp. 
 *               Returns JSX with conditional alignment and styling.
 * Inputs: Message object {content, sender, timestamp}.
 * Outputs: Rendered message bubble JSX.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */
```

#### 70. `frontend/src/components/ui/EgressAlert.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/ui/EgressAlert.tsx
 * Purpose: Emergency evacuation alert component - displays high-urgency 
 *          banner with evacuation message, nearest gate, animated ETA 
 *          countdown, alert sound.
 * Architecture: Modal-like alert with red styling, large text, animated timer. 
 *               Plays alert audio on mount. Dismissible but re-shows on new 
 *               evacuation event.
 * Inputs: Evacuation event (message, gate, ETA).
 * Outputs: Alert UI with high visual/audio salience.
 * Hackathon Vertical: Real-Time Decision Support & Accessibility
 * ===============================================================================
 */
```

### **Layout Components**

#### 71. `frontend/src/components/layout/Header.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/layout/Header.tsx
 * Purpose: Navigation header - displays fan name, match info, token expiry 
 *          warning, logout button.
 * Architecture: Always-visible header at top. Shows current fan name, match 
 *               name/time, token countdown (e.g., "Expires in 5 min"), logout.
 * Inputs: User context (name), JWT expiry time, match info.
 * Outputs: Header UI with user state and logout action.
 * Hackathon Vertical: Navigation & Authentication
 * ===============================================================================
 */
```

#### 72. `frontend/src/components/layout/StatusBar.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/layout/StatusBar.tsx
 * Purpose: Status bar - connection indicator, unread notifications counter, 
 *          current crowd density in user's section.
 * Architecture: Bottom status bar showing WebSocket connection status (green/red), 
 *               notification badge, section density percentage.
 * Inputs: WebSocket connection state, notifications, crowd data.
 * Outputs: Status bar UI with real-time indicators.
 * Hackathon Vertical: Real-Time Decision Support & Crowd Management
 * ===============================================================================
 */
```

### **Sidebar Components**

#### 73. `frontend/src/components/sidebar/Sidebar.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/sidebar/Sidebar.tsx
 * Purpose: Sidebar container - organizes multiple features into collapsible 
 *          tabs (navigation, transit, incidents, eco-vision). Orchestrates 
 *          TransitPanel, IncidentPanel, EcoVisionPanel.
 * Architecture: Tabbed interface with buttons for each feature. Active tab 
 *               shows content panel. Reduces screen clutter on mobile.
 * Inputs: Tab selection state.
 * Outputs: Active panel UI based on tab selection.
 * Hackathon Vertical: Navigation & Code Quality
 * ===============================================================================
 */
```

#### 74. `frontend/src/components/sidebar/EcoVisionPanel.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/sidebar/EcoVisionPanel.tsx
 * Purpose: Eco-vision camera UI - capture waste image, send to Gemini 
 *          classification, display result (type, bin color, eco fact), route 
 *          to nearest bin.
 * Architecture: Camera capture button, image preview, classification result 
 *               display. On submit: send base64 to backend → Gemini Vision 
 *               → show result + nearest bin route.
 * Inputs: Camera permission, image from user.
 * Outputs: Classification result, bin location, environmental fact.
 * Hackathon Vertical: Sustainability & Accessibility
 * ===============================================================================
 */
```

#### 75. `frontend/src/components/sidebar/IncidentPanel.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/sidebar/IncidentPanel.tsx
 * Purpose: Incident reporting UI - fan describes problem, category selector, 
 *          auto-triage via Gemini (severity, category, recommended action).
 * Architecture: Text input for description, category dropdown (medical, 
 *               security, facilities, other), submit button. On submit: send 
 *               to backend → Gemini triage → show result + dispatch status.
 * Inputs: Incident description, category hint.
 * Outputs: AI triage result (severity, category, action), dispatch confirmation.
 * Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
 * ===============================================================================
 */
```

#### 76. `frontend/src/components/sidebar/TransitPanel.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/sidebar/TransitPanel.tsx
 * Purpose: Transit selection UI - fan chooses transportation method 
 *          (metro/bus/rideshare/parking). Stores preference in state and 
 *          backend for route optimization.
 * Architecture: Four buttons (Metro, Bus, Rideshare, Parking) with active 
 *               state. On selection: POST preference → backend persists → 
 *               updates route computation.
 * Inputs: Transit preference selection.
 * Outputs: Stored preference in state and DB, updated exit routes.
 * Hackathon Vertical: Transportation & Navigation
 * ===============================================================================
 */
```

### **Shared Components**

#### 77. `frontend/src/components/shared/GlowButton.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/shared/GlowButton.tsx
 * Purpose: Styled button component - neon glow effect, consistent theming. 
 *          Used for Send, Submit, Call buttons across app.
 * Architecture: Reusable button with neon glow on hover. Props: children, 
 *               onClick, disabled state, variant (primary/secondary).
 * Inputs: Button props (label, onClick, disabled).
 * Outputs: Rendered button with glow styling.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */
```

#### 78. `frontend/src/components/shared/GlowCard.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/shared/GlowCard.tsx
 * Purpose: Styled card component - container with neon glow border. Used for 
 *          info boxes, alerts, POI details throughout app.
 * Architecture: Reusable card with glow border animation. Props: children, 
 *               variant (info/alert/success/error).
 * Inputs: Card children (content).
 * Outputs: Rendered card with glow border styling.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */
```

#### 79. `frontend/src/components/shared/TabButton.tsx`
```typescript
/**
 * ===============================================================================
 * File: frontend/src/components/shared/TabButton.tsx
 * Purpose: Tab button component - toggles between tabs in sidebar 
 *          (Nav, Transit, Incidents, Eco-Vision). Consistent styling.
 * Architecture: Button variant with active/inactive state styling. Props: 
 *               label, isActive, onClick.
 * Inputs: Tab selection.
 * Outputs: Rendered tab button with active state styling.
 * Hackathon Vertical: Accessibility & Code Quality
 * ===============================================================================
 */
```

---

## ✅ **ALL 79 FILES WITH HEADER COMMENTS**

You now have complete header comments for **every single file** in the repository. Simply:

1. **Copy** the header comment for the file
2. **Paste** at the very top of the file (above all imports)
3. **Repeat** for all 79 files
