#!/usr/bin/env sh
set -e

echo "[PREPARED] Waiting for PostgreSQL..."
python scripts/wait_for_postgres.py

echo "[PREPARED] Running database migrations..."
alembic upgrade head

echo "[PREPARED] Starting API server..."
exec uvicorn apps.api.main:app --host 0.0.0.0 --port 8000
