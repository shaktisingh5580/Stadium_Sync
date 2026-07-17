# ── Stadium Sync Backend — Production Dockerfile ──
# Multi-stage build optimized for Render deployment

# Stage 1: Builder — install dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runner — minimal production image
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/
# Include pre-populated demo database if it exists
COPY stadium_sync.db* ./

# Create non-root user for security and give it permissions
RUN adduser --disabled-password --no-create-home appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port (Render sets PORT env var)
EXPOSE 8000

# Health check for Render
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Start the application
# Render sets $PORT; we default to 8000 for local Docker
CMD uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 2 \
    --loop uvloop \
    --http httptools \
    --no-access-log
