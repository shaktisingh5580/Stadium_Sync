"""
===============================================================================
File: backend/app/main.py
Purpose: Core Backend Application Module.
Architecture: FastAPI backend module.
Inputs: standard API requests or internal service calls.
Outputs: structured responses/models.
Hackathon Vertical: Operational Intelligence & Real-Time Decision Support
===============================================================================
"""
"""
Stadium Sync — FastAPI Application Factory.

Creates and configures the FastAPI application with all middleware,
exception handlers, routes, and lifecycle hooks.

Deployment: Render runs `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import get_settings
from app.core.database import create_tables, dispose_engine
from app.core.exceptions import register_exception_handlers
from app.core.rate_limiter import setup_rate_limiter
from app.core.redis_client import close_redis, init_redis
from app.middleware.logging_mw import LoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Application Lifespan ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown lifecycle hooks.

    Startup:
    - Create database tables (dev mode)
    - Initialize Redis connection
    - Log configuration summary

    Shutdown:
    - Dispose database engine
    - Close Redis connection
    """
    # ── STARTUP ──
    logger.info(f"🏟️  Starting {settings.APP_NAME} v1.0.0")
    logger.info(f"   Environment: {settings.APP_ENV}")
    logger.info(f"   Debug: {settings.DEBUG}")

    # Create tables (dev only — production uses Alembic)
    if settings.is_development or settings.APP_ENV == "testing":
        await create_tables()

    # Initialize Redis
    await init_redis()

    logger.info(f"🚀 {settings.APP_NAME} is ready!")
    logger.info(f"   Docs: http://{settings.HOST}:{settings.PORT}/docs")

    yield

    # ── SHUTDOWN ──
    logger.info(f"🛑 Shutting down {settings.APP_NAME}...")
    await dispose_engine()
    await close_redis()
    logger.info("👋 Goodbye!")


# ── Create Application ──

app = FastAPI(
    title="Stadium Sync API",
    description=(
        "GenAI-Powered FIFA World Cup 2026 Operational Ecosystem. "
        "Transforms every fan's ticket into a personalized remote control "
        "and every volunteer into a geofenced rapid-responder."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# ── Middleware (order matters — last added = first executed) ──

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # The API uses Authorization headers, not browser cookies. Keeping this
    # false prevents cross-origin credential leakage.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time", "X-RateLimit-Limit"],
)

# Structured logging
app.add_middleware(LoggingMiddleware)

# Request ID injection
app.add_middleware(RequestIDMiddleware)

# Browser response hardening
app.add_middleware(SecurityHeadersMiddleware)

# ── Rate Limiter ──
setup_rate_limiter(app)

# ── Exception Handlers ──
register_exception_handlers(app)

# ── Routes ──
from app.api.v1.router import v1_router  # noqa: E402

app.include_router(v1_router, prefix=settings.API_V1_PREFIX)


# ── Root Endpoint ──

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint — redirects to docs."""
    return {
        "service": "Stadium Sync API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }
