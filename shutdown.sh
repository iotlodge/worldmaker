#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
mkdir -p logs

LOG="logs/shutdown.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "[$TIMESTAMP] Shutdown initiated" >> "$LOG"

echo "╔══════════════════════════════════════╗"
echo "║        WorldMaker Shutdown           ║"
echo "╚══════════════════════════════════════╝"
echo ""

ERRORS=0

# ── [1] Stop Frontend ────────────────────────────────────────────────────
echo "[1/4] Stopping frontend (Next.js)..."
if pkill -f "next dev" 2>/dev/null; then
  echo "       ✓ Frontend stopped"
  echo "[$TIMESTAMP] Frontend stopped (next dev)" >> "$LOG"
else
  echo "       – Not running"
fi
pkill -f "next-server" 2>/dev/null || true

# Also kill by port if pkill missed it
if lsof -ti:3000 > /dev/null 2>&1; then
  lsof -ti:3000 | xargs kill 2>/dev/null || true
  echo "       ✓ Port 3000 cleaned up"
  echo "[$TIMESTAMP] Port 3000 force-cleaned" >> "$LOG"
fi

# ── [2] Stop API ─────────────────────────────────────────────────────────
echo "[2/4] Stopping API server..."
if pkill -f "worldmaker serve" 2>/dev/null; then
  echo "       ✓ API stopped"
  echo "[$TIMESTAMP] API stopped (worldmaker serve)" >> "$LOG"
else
  echo "       – Not running"
fi
pkill -f "uvicorn.*worldmaker" 2>/dev/null || true

# Also kill by port if pkill missed it
if lsof -ti:8000 > /dev/null 2>&1; then
  lsof -ti:8000 | xargs kill 2>/dev/null || true
  echo "       ✓ Port 8000 cleaned up"
  echo "[$TIMESTAMP] Port 8000 force-cleaned" >> "$LOG"
fi

# ── [3] Stop Worker ──────────────────────────────────────────────────────
echo "[3/4] Stopping Celery worker..."
if pkill -f "celery.*worldmaker" 2>/dev/null; then
  echo "       ✓ Worker stopped"
  echo "[$TIMESTAMP] Worker stopped" >> "$LOG"
else
  echo "       – Not running"
fi

# ── [4] Stop Infrastructure ──────────────────────────────────────────────
echo "[4/4] Stopping infrastructure..."
if docker compose ps -q 2>/dev/null | grep -q .; then
  if docker compose down >> "$LOG" 2>&1; then
    echo "       ✓ Infrastructure stopped"
    echo "[$TIMESTAMP] Docker infrastructure stopped" >> "$LOG"
  else
    echo "       ⚠ Error stopping infrastructure — see logs/shutdown.log" >&2
    echo "[$TIMESTAMP] ERROR: docker compose down failed" >> "$LOG"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "       – No containers running"
fi

# ── Final status ─────────────────────────────────────────────────────────
echo ""
if [ "$ERRORS" -gt 0 ]; then
  echo "Shutdown complete with $ERRORS error(s). Check logs/shutdown.log."
  echo "[$TIMESTAMP] Shutdown complete with $ERRORS error(s)" >> "$LOG"
else
  echo "All services stopped."
  echo "[$TIMESTAMP] Shutdown complete — clean" >> "$LOG"
fi
