# Kometa Web UI Dockerfile
# Multi-stage build for the Web UI container

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt


# Final stage
FROM python:3.11-slim

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    KOMETA_CONFIG_DIR=/config \
    KOMETA_UI_PORT=8080 \
    KOMETA_UI_HOST=0.0.0.0 \
    KOMETA_UI_APPLY_ENABLED=false

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r kometa && useradd -r -g kometa kometa

# Create directories
RUN mkdir -p /config /app && chown -R kometa:kometa /config /app

WORKDIR /app

# Copy application files
COPY --chown=kometa:kometa backend/ /app/backend/
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
