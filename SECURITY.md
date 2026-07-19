# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | ✅ Current release |

## Reporting a Vulnerability

If you discover a security vulnerability in Stadium Sync, please report it responsibly:

1. **Email**: shaktisingh4140@gmail.com
2. **Subject line**: `[SECURITY] Stadium Sync — <brief description>`
3. **Include**: Steps to reproduce, affected components, and potential impact.

We will acknowledge receipt within 48 hours and provide an initial assessment within 7 business days.

**Please do NOT open a public GitHub issue for security vulnerabilities.**

## Security Architecture

Stadium Sync implements defense-in-depth security across multiple layers:

### Authentication & Authorization

| Control | Implementation |
|---------|---------------|
| **Token Authentication** | HS256 JWT with 4-hour expiry tied to match duration |
| **QR Ticket Integrity** | HMAC-SHA256 checksums prevent payload forgery |
| **Role-Based Access** | `fan`, `volunteer`, `admin` roles enforced at middleware |
| **IoT Authentication** | Separate `X-API-Key` header for sensor endpoints |

### Input Validation

| Control | Implementation |
|---------|---------------|
| **Schema Validation** | Pydantic v2 models with `min_length`, `max_length`, regex patterns |
| **File Upload** | Base64-encoded images with size limits for Eco-Vision |
| **SQL Injection** | Parameterized queries via SQLAlchemy ORM (no raw SQL) |
| **XSS Prevention** | React's default JSX escaping + CSP headers |

### Transport & Network Security

| Control | Implementation |
|---------|---------------|
| **HTTPS** | Enforced via Render TLS termination |
| **CORS** | Explicit origin allowlist — no wildcards in production |
| **Security Headers** | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Content-Security-Policy` |
| **Request Tracing** | UUID-based `X-Request-ID` on every request |

### Rate Limiting

| Endpoint Category | Limit |
|-------------------|-------|
| General API | 60/minute |
| Authentication | 10/minute |
| AI/Gemini | 20/minute |
| File Upload | 10/minute |
| IoT Sensors | 300/minute |

### Container Security

- **Non-root execution**: Dockerfile creates `appuser` — container never runs as root
- **Multi-stage build**: Build dependencies excluded from production image
- **Minimal base image**: `python:3.12-slim` with no unnecessary packages
- **Read-only principles**: Application code owned by non-root user

### Production Configuration Validation

The `Settings.validate_production_security()` model validator **refuses to start** the application if any of the following are true:
- `DEBUG=true`
- `SECRET_KEY` shorter than 32 characters
- `CORS_ORIGINS` contains `*`
- `ALLOW_AI_MOCK_FALLBACK=true`
- `ALLOW_DEMO_FEATURES=true`

### Dependency Management

- Backend: `pip audit` for Python dependency vulnerability scanning
- Frontend: `npm audit --audit-level=high` for Node.js dependencies
- GitHub: CodeQL static analysis on every push

## Known Limitations

1. **SQLite in demo mode**: The hackathon demo uses SQLite which does not support concurrent writes at scale. Production would use PostgreSQL (Neon Serverless).
2. **No OAuth/OIDC**: Authentication uses custom JWT tokens rather than a federated identity provider. Production would integrate with Firebase Auth or Google Identity Platform.
3. **WebSocket scaling**: The in-memory WebSocket manager is single-instance. Production would use Redis Pub/Sub for multi-instance coordination.
