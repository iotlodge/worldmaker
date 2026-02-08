#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
mkdir -p logs

# ── Parse flags ──────────────────────────────────────────────────────────
NO_INFRA=false
NO_FRONTEND=false
API_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --no-infra)    NO_INFRA=true ;;
    --no-frontend) NO_FRONTEND=true ;;
    --api-only)    API_ONLY=true; NO_INFRA=true; NO_FRONTEND=true ;;
    --help|-h)
      echo "Usage: ./start.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --no-infra      Skip Docker infrastructure (use existing or in-memory only)"
      echo "  --no-frontend   Skip Next.js frontend"
      echo "  --api-only      Start only the API server (no infra, no frontend)"
      echo "  --help          Show this help"
      echo ""
      echo "Default: starts infrastructure → worker → API → frontend"
      exit 0
      ;;
  esac
done

echo "╔══════════════════════════════════════╗"
echo "║        WorldMaker Startup            ║"
echo "╚══════════════════════════════════════╝"
echo ""

STEP=1
TOTAL=4
if $NO_INFRA; then TOTAL=$((TOTAL - 1)); fi
if $NO_FRONTEND; then TOTAL=$((TOTAL - 1)); fi

# ── [1] Infrastructure ───────────────────────────────────────────────────
if ! $NO_INFRA; then
  echo "[$STEP/$TOTAL] Starting infrastructure..."
  docker compose up -d postgres mongodb neo4j redis kafka zookeeper

  echo "         Waiting for services to be healthy..."
  SERVICES=(postgres mongodb neo4j redis)
  MAX_WAIT=60

  for svc in "${SERVICES[@]}"; do
    ELAPSED=0
    while true; do
      STATUS=$(docker compose ps "$svc" --format json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list): data = data[0]
    print(data.get('Health', data.get('State', 'unknown')))
except: print('unknown')
" 2>/dev/null || echo "unknown")

      if [[ "$STATUS" == *"healthy"* ]]; then
        echo "         ✓ $svc ready"
        break
      fi

      if (( ELAPSED >= MAX_WAIT )); then
        echo "         ⚠ $svc not healthy after ${MAX_WAIT}s — continuing anyway"
        break
      fi

      sleep 2
      ELAPSED=$((ELAPSED + 2))
    done
  done

  # Run migrations if Postgres is up
  echo "         Running database migrations..."
  if uv run alembic upgrade head 2>/dev/null; then
    echo "         ✓ Migrations applied"
  else
    echo "         ⚠ Migration failed (non-fatal, in-memory store still works)"
  fi

  STEP=$((STEP + 1))
fi

# ── [2] Celery Worker ────────────────────────────────────────────────────
echo "[$STEP/$TOTAL] Starting Celery worker..."
if docker compose up -d worldmaker-worker 2>/dev/null; then
  echo "         ✓ Worker started (Docker)"
else
  if command -v celery &>/dev/null; then
    nohup uv run celery -A worldmaker.engine.scheduler worker \
      --loglevel=info > logs/worker.log 2>&1 &
    echo "         ✓ Worker started (local, PID: $!)"
  else
    echo "         ⚠ Celery not available — using AsyncScheduler fallback"
  fi
fi
STEP=$((STEP + 1))

# ── [3] Frontend (background) ────────────────────────────────────────────
if ! $NO_FRONTEND; then
  echo "[$STEP/$TOTAL] Starting frontend (Next.js)..."
  if [ -d "$SCRIPT_DIR/frontend" ] && [ -f "$SCRIPT_DIR/frontend/package.json" ]; then
    # Install deps if node_modules missing
    if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
      echo "         Installing frontend dependencies..."
      (cd "$SCRIPT_DIR/frontend" && npm install --silent) || true
    fi
    # Start dev server in background
    nohup npm --prefix "$SCRIPT_DIR/frontend" run dev > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "         ✓ Frontend started (PID: $FRONTEND_PID, http://localhost:3000)"
    echo "         Log: logs/frontend.log"
  else
    echo "         ⚠ frontend/ directory not found — skipping"
  fi
  STEP=$((STEP + 1))
fi

# ── [4] API Server (foreground) ──────────────────────────────────────────
echo "[$STEP/$TOTAL] Starting API server..."
echo ""
echo "┌──────────────────────────────────────────────────────┐"
echo "│  API:      http://localhost:8000                     │"
echo "│  Docs:     http://localhost:8000/api/docs            │"
if ! $NO_FRONTEND; then
echo "│  Frontend: http://localhost:3000                     │"
fi
echo "│                                                      │"
echo "│  Press Ctrl+C to stop the API server.                │"
echo "│  Run ./shutdown.sh to stop everything.               │"
echo "└──────────────────────────────────────────────────────┘"
echo ""

uv run worldmaker serve --reload
