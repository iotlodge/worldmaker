#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════╗"
echo "║        WorldMaker Restart            ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Stop everything ──────────────────────────────────────────────────────
echo "Stopping all services..."
pkill -f "next dev" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true
pkill -f "worldmaker serve" 2>/dev/null || true
pkill -f "uvicorn.*worldmaker" 2>/dev/null || true
pkill -f "celery.*worldmaker" 2>/dev/null || true
docker compose stop worldmaker-api worldmaker-worker 2>/dev/null || true
sleep 2

# ── Restart infrastructure ───────────────────────────────────────────────
echo "Ensuring infrastructure is up..."
docker compose up -d postgres mongodb neo4j redis kafka zookeeper 2>/dev/null || true

# ── Delegate to start.sh ─────────────────────────────────────────────────
echo ""
exec "$SCRIPT_DIR/start.sh" "$@"
