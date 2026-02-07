#!/bin/bash
# Run the backend in the foreground so you can see errors. Use this to debug.
# In another terminal run: npm run start-frontend
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
source ./venv/bin/activate
echo "Starting backend at http://127.0.0.1:8000 (Ctrl+C to stop)"
exec ./venv/bin/python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 --reload-dir backend
