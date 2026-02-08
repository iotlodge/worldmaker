#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
mkdir -p logs

echo "╔══════════════════════════════════════╗"
echo "║        WorldMaker Restart            ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Shutdown ─────────────────────────────────────────────────────────────
echo "Phase 1: Stopping all services..."
echo ""

# Delegate to shutdown.sh for clean teardown with logging
"$SCRIPT_DIR/shutdown.sh"

echo ""
echo "Phase 2: Starting all services..."
echo ""

# Brief pause to let ports release
sleep 2

# ── Startup ──────────────────────────────────────────────────────────────
# Pass through any flags (--no-infra, --no-frontend, --api-only, --no-browser)
exec "$SCRIPT_DIR/start.sh" "$@"
