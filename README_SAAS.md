# PREPARED.ai SaaS Runtime

## Start locally

```bash
cp .env.example .env

docker compose up --build
```

## API endpoints

GET /health
POST /v1/evaluations/run
GET /v1/evaluations/{job_id}
GET /v1/evaluations/{job_id}/report
GET /v1/evaluations/{job_id}/points
DELETE /v1/evaluations/{job_id}

## Current architecture

Frontend (Next.js)
↓
FastAPI Gateway
↓
Redis Queue
↓
Celery Worker
↓
PREPARED evaluation kit

## CI

PREPARED SaaS CI validates the API import path and frontend build on pushes to main.
