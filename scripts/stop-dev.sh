#!/bin/bash
#
# Kometa Web UI - Development Stop Script
#
# This script stops the Web UI development containers.
#
# Usage:
#   ./scripts/stop-dev.sh
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBUI_DIR="$PROJECT_ROOT/webui"

echo "Stopping Kometa Web UI containers..."

cd "$WEBUI_DIR"
docker-compose down

echo "Containers stopped."
