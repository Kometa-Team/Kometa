# Kometa Web UI Dockerfile
# Multi-stage build with Vue 3 frontend

# ===========================================
# Stage 1: Build Vue Frontend
# ===========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies first (better caching)
COPY frontend-vue/package*.json ./
RUN npm ci --prefer-offline

# Copy source and build
COPY frontend-vue/ ./
RUN npm run build


# ===========================================
# Stage 2: Python Dependencies
# ===========================================
FROM python:3.11-slim AS python-builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Web UI dependencies
COPY backend/requirements.txt /tmp/webui-requirements.txt
RUN pip install --no-cache-dir -r /tmp/webui-requirements.txt

# Install Kometa dependencies (for running kometa.py)
COPY kometa-requirements.txt /tmp/kometa-requirements.txt
RUN pip install --no-cache-dir -r /tmp/kometa-requirements.txt


# ===========================================
# Stage 3: Final Image
# ===========================================
FROM python:3.11-slim

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    KOMETA_CONFIG_DIR=/config \
    KOMETA_ROOT=/kometa \
    KOMETA_UI_PORT=8080 \
    KOMETA_UI_HOST=0.0.0.0 \
    KOMETA_UI_APPLY_ENABLED=false \
    KOMETA_UI_MODE=vue

# Copy virtual environment from builder
COPY --from=python-builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r kometa && useradd -r -g kometa kometa

# Create directories
RUN mkdir -p /config /app /kometa && chown -R kometa:kometa /config /app

WORKDIR /app

# Copy backend application
COPY --chown=kometa:kometa backend/ /app/backend/

# Copy built Vue frontend
COPY --from=frontend-builder --chown=kometa:kometa /app/frontend/dist /app/frontend-vue/dist

# Copy legacy frontend (for fallback)
COPY --chown=kometa:kometa frontend/ /app/frontend/

# Switch to non-root user
USER kometa

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health')" || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8080"]
