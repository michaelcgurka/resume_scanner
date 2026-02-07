#!/bin/bash

set -e  # stop script on errors

# Always run from repo root (so "npm start" from frontend/ still finds venv and backend)
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

source ./venv/bin/activate

timeout 2 pkill -f "uvicorn backend.app.main" 2>/dev/null || true

./venv/bin/python -m uvicorn backend.app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --reload-dir backend > backend.log 2>&1 &

BACKEND_PID=$!
echo "Waiting for backend to bind to port 8000..."
for i in 1 2 3 4 5 6 7 8 9 10; do
  sleep 1
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend process exited. Logs:"
    cat backend.log
    exit 1
  fi
  if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health 2>/dev/null | grep -q 200; then
    echo "Backend ready at http://127.0.0.1:8000 (PID $BACKEND_PID)"
    break
  fi
  if [ "$i" -eq 10 ]; then
    echo "Backend did not respond after 10s. Logs:"
    cat backend.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
  fi
done
echo "Starting frontend (Create React App compile may take 1-3+ min on Windows filesystem)..."

cd "$ROOT/frontend"
./node_modules/.bin/react-scripts start

kill $BACKEND_PID 2>/dev/null || true
