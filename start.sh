#!/bin/bash
# Resume Scanner dev startup (backend + frontend).
# SLOW START ROOT CAUSE: The long wait is the frontend — Create React App's
# webpack compile. If this project lives on the Windows filesystem (e.g.
# /mnt/c/...) under WSL, I/O is very slow and the first compile can take
# 1–3+ minutes. Backend starts in ~1s. Best fix: move the project to your
# WSL Linux filesystem (e.g. ~/resume_scanner) and reinstall deps there.
set -e  # stop script on errors

# Activate virtual environment
source ./venv/bin/activate

# Kill old backend (safe for dev); cap at 2s so startup never hangs
timeout 2 pkill -f "uvicorn backend.app.main" 2>/dev/null || true

# Start backend in background
./venv/bin/python -m uvicorn backend.app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --reload-dir backend > backend.log 2>&1 &

BACKEND_PID=$!
# Give uvicorn a moment to bind and load the app
sleep 1
echo "Backend started (PID $BACKEND_PID) in ~1s, logs in backend.log"
echo "Starting frontend (Create React App compile is the slow part; may take 1-3+ min on Windows filesystem)..."

# Start frontend in foreground (use local bin to avoid npx resolution delay)
cd frontend
./node_modules/.bin/react-scripts start

# Kill backend when frontend exits
kill $BACKEND_PID
