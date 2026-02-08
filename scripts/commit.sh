#!/usr/bin/env bash
# Usage: ./scripts/commit.sh "your commit message"
# Stages all changes, commits with the given message, and pushes to origin.

set -euo pipefail

MSG="${1:?Usage: $0 \"commit message\"}"

cd "$(dirname "$0")/.."

git add -A
git commit -m "$MSG"
git push
