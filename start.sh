#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
mkdir -p logs

# ── Parse flags ──────────────────────────────────────────────────────────
NO_INFRA=false
NO_FRONTEND=false
API_ONLY=false
NO_BROWSER=false

for arg in "$@"; do
  case "$arg" in
    --no-infra)    NO_INFRA=true ;;
    --no-frontend) NO_FRONTEND=true ;;
    --api-only)    API_ONLY=true; NO_INFRA=true; NO_FRONTEND=true ;;
    --no-browser)  NO_BROWSER=true ;;
    --help|-h)
      echo "Usage: ./start.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --no-infra      Skip Docker infrastructure (use existing or in-memory only)"
      echo "  --no-frontend   Skip Next.js frontend"
      echo "  --api-only      Start only the API server (no infra, no frontend)"
      echo "  --no-browser    Don't auto-open browser on startup"
      echo "  --help          Show this help"
      echo ""
      echo "Default: starts infrastructure → worker → API → frontend → opens browser"
      exit 0
      ;;
  esac
done

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

echo "╔══════════════════════════════════════╗"
echo "║        WorldMaker Startup            ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  Logs: $SCRIPT_DIR/logs/"
echo ""

STEP=1
TOTAL=4
if $NO_INFRA; then TOTAL=$((TOTAL - 1)); fi
if $NO_FRONTEND; then TOTAL=$((TOTAL - 1)); fi

# ── [1] Infrastructure ───────────────────────────────────────────────────
if ! $NO_INFRA; then
  echo "[$STEP/$TOTAL] Starting infrastructure..."
  docker compose up -d postgres mongodb neo4j redis kafka zookeeper \
    >> logs/infra.log 2>&1

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
        echo "         ⚠ $svc not healthy after ${MAX_WAIT}s — continuing anyway" | tee -a logs/infra-error.log
        break
      fi

      sleep 2
      ELAPSED=$((ELAPSED + 2))
    done
  done

  # Run migrations if Postgres is up
  echo "         Running database migrations..."
  if uv run alembic upgrade head >> logs/infra.log 2>&1; then
    echo "         ✓ Migrations applied"
  else
    echo "         ⚠ Migration failed (non-fatal, in-memory store still works)" | tee -a logs/infra-error.log
  fi

  STEP=$((STEP + 1))
fi

# ── [2] Celery Worker ────────────────────────────────────────────────────
echo "[$STEP/$TOTAL] Starting Celery worker..."
if docker compose up -d worldmaker-worker >> logs/worker.log 2>&1; then
  echo "         ✓ Worker started (Docker)"
else
  if command -v celery &>/dev/null; then
    nohup uv run celery -A worldmaker.engine.scheduler worker \
      --loglevel=info >> logs/worker.log 2>> logs/worker-error.log &
    echo "         ✓ Worker started (local, PID: $!)"
  else
    echo "         ⚠ Celery not available — using AsyncScheduler fallback"
  fi
fi
STEP=$((STEP + 1))

# ── [3] API Server (background) ─────────────────────────────────────────
echo "[$STEP/$TOTAL] Starting API server..."
nohup uv run worldmaker serve --reload \
  >> logs/api.log 2>> logs/api-error.log &
API_PID=$!
echo "         PID: $API_PID"
echo "         Log: logs/api.log | Errors: logs/api-error.log"

# Wait for API to be ready
echo -n "         Waiting for API"
API_READY=false
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    API_READY=true
    break
  fi
  echo -n "."
  sleep 1
done
echo ""

if $API_READY; then
  echo "         ✓ API server ready (http://localhost:8000)"
else
  echo "         ⚠ API not responding yet — check logs/api-error.log" | tee -a logs/api-error.log
  echo "           (server may still be starting, give it a moment)"
fi
STEP=$((STEP + 1))

# ── [4] Frontend (background) ────────────────────────────────────────────
FRONTEND_READY=false
if ! $NO_FRONTEND; then
  echo "[$STEP/$TOTAL] Starting frontend (Next.js)..."
  if [ -d "$SCRIPT_DIR/frontend" ] && [ -f "$SCRIPT_DIR/frontend/package.json" ]; then
    # Install deps if node_modules missing
    if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
      echo "         Installing frontend dependencies..."
      (cd "$SCRIPT_DIR/frontend" && npm install --silent) >> logs/frontend.log 2>&1 || true
    fi
    # Start dev server in background
    nohup npm --prefix "$SCRIPT_DIR/frontend" run dev \
      >> logs/frontend.log 2>> logs/frontend-error.log &
    FRONTEND_PID=$!
    echo "         PID: $FRONTEND_PID"
    echo "         Log: logs/frontend.log | Errors: logs/frontend-error.log"

    # Wait for frontend to be ready
    echo -n "         Waiting for frontend"
    for i in $(seq 1 30); do
      if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        FRONTEND_READY=true
        break
      fi
      echo -n "."
      sleep 1
    done
    echo ""

    if $FRONTEND_READY; then
      echo "         ✓ Frontend ready (http://localhost:3000)"
    else
      echo "         ⚠ Frontend not responding yet — check logs/frontend-error.log" | tee -a logs/frontend-error.log
    fi
  else
    echo "         ⚠ frontend/ directory not found — skipping"
  fi
  STEP=$((STEP + 1))
fi

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
echo "┌──────────────────────────────────────────────────────┐"
echo "│  WorldMaker is running                               │"
echo "│                                                      │"
echo "│  API:      http://localhost:8000                     │"
echo "│  Docs:     http://localhost:8000/api/docs            │"
if ! $NO_FRONTEND; then
echo "│  Frontend: http://localhost:3000                     │"
fi
echo "│                                                      │"
echo "│  Logs:     $SCRIPT_DIR/logs/              │"
echo "│  Stop:     ./shutdown.sh                             │"
echo "└──────────────────────────────────────────────────────┘"
echo ""

# ── Open browser & bring to foreground ───────────────────────────────────
if ! $NO_BROWSER; then
  LANDING="http://localhost:3000"
  if $NO_FRONTEND; then
    LANDING="http://localhost:8000/api/docs"
  fi

  if [[ "$(uname)" == "Darwin" ]]; then
    # macOS: open in default browser and bring to front
    open "$LANDING"
    sleep 0.5
    osascript -e '
      tell application "System Events"
        set frontApp to name of first application process whose frontmost is true
      end tell
      if frontApp is not "Safari" and frontApp is not "Google Chrome" and frontApp is not "Firefox" and frontApp is not "Arc" then
        try
          tell application "Google Chrome" to activate
        on error
          try
            tell application "Safari" to activate
          end try
        end try
      end if
    ' 2>/dev/null || true
    echo "  ✓ Browser opened → $LANDING"
  elif command -v xdg-open &>/dev/null; then
    # Linux
    xdg-open "$LANDING" 2>/dev/null &
    echo "  ✓ Browser opened → $LANDING"
  else
    echo "  → Open $LANDING in your browser"
  fi
fi

echo ""
echo "All processes running in background. Use ./shutdown.sh to stop."
