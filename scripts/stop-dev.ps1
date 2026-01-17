# Kometa Web UI - Development Stop Script (PowerShell)
#
# This script stops the Web UI development containers.
#
# Usage:
#   .\scripts\stop-dev.ps1
#

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$WebUIDir = Join-Path $ProjectRoot "webui"

Write-Host "Stopping Kometa Web UI containers..."

Set-Location $WebUIDir
docker-compose down

Write-Host "Containers stopped."
