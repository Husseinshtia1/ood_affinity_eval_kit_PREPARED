# PREPARED.ai DigitalOcean Deployment Plan

This document describes how to run PREPARED.ai on DigitalOcean.

## Recommended options

### Option A — DigitalOcean App Platform

Use this when you want managed deployment from GitHub with minimal server administration.

Recommended components:

- API service built from `Dockerfile.api`
- Frontend service built from `Dockerfile.frontend`
- Worker service built from `Dockerfile.worker`
- Managed PostgreSQL database
- Managed Redis database, if available for the selected plan/region
- Spaces or external S3-compatible storage for reports/artifacts

### Option B — DigitalOcean Droplet with Docker Compose

Use this when you want full control and predictable VPS pricing.

Recommended components:

- Ubuntu Droplet
- Docker Engine
- Docker Compose
- `docker-compose.prod.yml`
- Nginx reverse proxy
- Let's Encrypt TLS certificates
- Managed PostgreSQL or local PostgreSQL volume
- Managed Redis or local Redis volume

## App Platform environment variables

Set these for the API service:

```env
ENVIRONMENT=development
APP_NAME=PREPARED.ai API Gateway
APP_VERSION=0.1.0-p0
DATABASE_URL=replace-with-managed-postgres-url
FRONTEND_URL=https://your-frontend-domain
JWT_SECRET_KEY=replace-with-secure-secret
TEMP_STORAGE_DIR=/tmp/prepared_jobs
MAX_UPLOAD_BYTES=26214400
REPORT_TTL_MINUTES=60
SMTP_FROM_EMAIL=no-reply@example.com
ALLOWED_ORIGINS=https://your-frontend-domain
```

For the frontend service:

```env
NEXT_PUBLIC_API_URL=https://your-api-domain
```

For the worker service, add:

```env
REDIS_URL=replace-with-redis-url
CELERY_BROKER_URL=replace-with-redis-url
CELERY_RESULT_BACKEND=replace-with-redis-url
```

## Droplet deployment baseline

1. Create Ubuntu Droplet.
2. Install Docker and Docker Compose.
3. Clone the repository.
4. Create `.env.production` from `env.production.example`.
5. Replace all placeholder secrets.
6. Run:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

7. Verify:

```bash
curl http://SERVER_IP:8000/health
```

## Production hardening checklist

- Use strong secrets.
- Use managed PostgreSQL or configure reliable backups.
- Use managed Redis or configure persistence.
- Run migrations as a controlled step.
- Put API and frontend behind HTTPS.
- Configure CORS to the real frontend domain.
- Configure SMTP provider.
- Configure S3/Spaces storage.
- Enable monitoring and logs.
- Complete legal/security review before real customer data.

## Current status

Railway already verified a live API baseline. DigitalOcean can now become the production target if desired.
