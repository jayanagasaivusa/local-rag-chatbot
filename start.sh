#!/usr/bin/env bash
# Convenience script: starts the FastAPI backend and Vite frontend together.
# Requires: backend/venv already created (see README), frontend node_modules installed.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
  echo "Shutting down..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting FastAPI backend on http://localhost:8000 ..."
(
  cd "$ROOT_DIR/backend"
  source venv/bin/activate
  uvicorn main:app --reload --port 8000
) &
BACKEND_PID=$!

echo "Starting Vite frontend on http://localhost:5173 ..."
(
  cd "$ROOT_DIR/frontend"
  npm run dev
) &
FRONTEND_PID=$!

wait "$BACKEND_PID" "$FRONTEND_PID"
