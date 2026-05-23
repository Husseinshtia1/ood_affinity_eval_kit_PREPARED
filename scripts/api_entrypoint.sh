#!/usr/bin/env sh
set -e

echo "[PREPARED] Starting API server..."
exec uvicorn apps.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
