#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════╗"
echo "║        WorldMaker Shutdown           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── [1] Stop Frontend ────────────────────────────────────────────────────
echo "[1/4] Stopping frontend (Next.js)..."
pkill -f "next dev" 2>/dev/null && echo "       ✓ Frontend stopped" || echo "       – Not running"
pkill -f "next-server" 2>/dev/null || true

# ── [2] Stop API ─────────────────────────────────────────────────────────
echo "[2/4] Stopping API server..."
pkill -f "worldmaker serve" 2>/dev/null && echo "       ✓ API stopped" || echo "       – Not running"
pkill -f "uvicorn.*worldmaker" 2>/dev/null || true

# ── [3] Stop Worker ──────────────────────────────────────────────────────
echo "[3/4] Stopping Celery worker..."
pkill -f "celery.*worldmaker" 2>/dev/null && echo "       ✓ Worker stopped" || echo "       – Not running"

# ── [4] Stop Infrastructure ──────────────────────────────────────────────
echo "[4/4] Stopping infrastructure..."
if docker compose ps -q 2>/dev/null | grep -q .; then
  docker compose down
  echo "       ✓ Infrastructure stopped"
else
  echo "       – No containers running"
fi

echo ""
echo "All services stopped."
