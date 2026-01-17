#!/bin/bash
#
# Kometa Web UI - Development Startup Script
#
# This script starts the Web UI in development mode using Docker Compose.
#
# Usage:
#   ./scripts/start-dev.sh
#
# Environment variables (optional):
#   KOMETA_CONFIG_PATH  - Path to config directory (default: ./config)
#   KOMETA_UI_PORT      - Port for the UI (default: 8080)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBUI_DIR="$PROJECT_ROOT/webui"

echo "========================================"
echo "Kometa Web UI - Development Mode"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker first."
    exit 1
fi

# Create config directory if it doesn't exist
CONFIG_PATH="${KOMETA_CONFIG_PATH:-$PROJECT_ROOT/config}"
mkdir -p "$CONFIG_PATH"
mkdir -p "$CONFIG_PATH/backups"
mkdir -p "$CONFIG_PATH/logs/runs"

echo "Config directory: $CONFIG_PATH"
echo ""

# Set environment variables for docker-compose
export KOMETA_CONFIG_PATH="$CONFIG_PATH"
export KOMETA_SOURCE_PATH="$PROJECT_ROOT"
export KOMETA_UI_APPLY_ENABLED="${KOMETA_UI_APPLY_ENABLED:-false}"

# Change to webui directory
cd "$WEBUI_DIR"

# Build and start containers
echo "Building and starting containers..."
docker-compose up --build -d

# Wait for the UI to be ready
echo ""
echo "Waiting for UI to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
        echo ""
        echo "========================================"
        echo "Kometa Web UI is ready!"
        echo ""
        echo "  URL: http://localhost:8080"
        echo ""
        echo "  Mode: ${KOMETA_UI_APPLY_ENABLED:-DRY RUN ONLY}"
        echo ""
        echo "To stop: ./scripts/stop-dev.sh"
        echo "To view logs: docker-compose -f webui/docker-compose.yml logs -f"
        echo "========================================"
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo ""
echo "WARNING: UI may not be fully ready. Check logs with:"
echo "  docker-compose -f webui/docker-compose.yml logs"
