# Kometa Web UI - Development Startup Script (PowerShell)
#
# This script starts the Web UI in development mode using Docker Compose.
#
# Usage:
#   .\scripts\start-dev.ps1
#
# Environment variables (optional):
#   $env:KOMETA_CONFIG_PATH  - Path to config directory (default: ./config)
#   $env:KOMETA_UI_PORT      - Port for the UI (default: 8080)
#

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$WebUIDir = Join-Path $ProjectRoot "webui"

Write-Host "========================================"
Write-Host "Kometa Web UI - Development Mode"
Write-Host "========================================"
Write-Host ""

# Check if Docker is running
try {
    docker info 2>&1 | Out-Null
} catch {
    Write-Host "ERROR: Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Create config directory if it doesn't exist
$ConfigPath = if ($env:KOMETA_CONFIG_PATH) { $env:KOMETA_CONFIG_PATH } else { Join-Path $ProjectRoot "config" }
New-Item -ItemType Directory -Force -Path $ConfigPath | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ConfigPath "backups") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $ConfigPath "logs\runs") | Out-Null

Write-Host "Config directory: $ConfigPath"
Write-Host ""

# Set environment variables for docker-compose
$env:KOMETA_CONFIG_PATH = $ConfigPath
$env:KOMETA_SOURCE_PATH = $ProjectRoot
if (-not $env:KOMETA_UI_APPLY_ENABLED) {
    $env:KOMETA_UI_APPLY_ENABLED = "false"
}

# Change to webui directory
Set-Location $WebUIDir

# Build and start containers
Write-Host "Building and starting containers..."
docker-compose up --build -d

# Wait for the UI to be ready
Write-Host ""
Write-Host "Waiting for UI to be ready..."
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/api/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host ""
            Write-Host "========================================"
            Write-Host "Kometa Web UI is ready!" -ForegroundColor Green
            Write-Host ""
            Write-Host "  URL: http://localhost:8080"
            Write-Host ""
            Write-Host "  Mode: $($env:KOMETA_UI_APPLY_ENABLED -eq 'true' ? 'APPLY ENABLED' : 'DRY RUN ONLY')"
            Write-Host ""
            Write-Host "To stop: .\scripts\stop-dev.ps1"
            Write-Host "To view logs: docker-compose -f webui/docker-compose.yml logs -f"
            Write-Host "========================================"
            exit 0
        }
    } catch {
        # Ignore errors, keep waiting
    }
    Start-Sleep -Seconds 1
    Write-Host -NoNewline "."
}

Write-Host ""
Write-Host "WARNING: UI may not be fully ready. Check logs with:" -ForegroundColor Yellow
Write-Host "  docker-compose -f webui/docker-compose.yml logs"
