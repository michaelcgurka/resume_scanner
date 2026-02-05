#!/bin/bash

set -e  # stop script on errors

source ./venv/bin/activate

timeout 2 pkill -f "uvicorn backend.app.main" 2>/dev/null || true

./venv/bin/python -m uvicorn backend.app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --reload-dir backend > backend.log 2>&1 &

BACKEND_PID=$!
sleep 1
echo "Backend started (PID $BACKEND_PID) in ~1s, logs in backend.log"
echo "Starting frontend (Create React App compile is the slow part; may take 1-3+ min on Windows filesystem)..."

cd frontend
./node_modules/.bin/react-scripts start

kill $BACKEND_PID
