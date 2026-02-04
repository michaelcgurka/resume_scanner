# Multi-stage: build frontend, then run backend serving it
FROM node:20-bookworm-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --omit=dev
COPY frontend/ .
# Build with production API URL placeholder; override at build time via ARG
ARG REACT_APP_API_URL=
ARG REACT_APP_API_KEY=
ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_API_KEY=$REACT_APP_API_KEY
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
# Install system deps if needed (e.g. for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/build ./frontend/build/
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
# Production: no --reload
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
