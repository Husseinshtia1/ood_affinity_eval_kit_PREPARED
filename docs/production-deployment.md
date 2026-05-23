# PREPARED.ai Production Deployment

This document describes the production Docker deployment path for PREPARED.ai.

## Components

The production stack includes:

- API service built from `Dockerfile.api`
- Celery worker built from `Dockerfile.worker`
- PostgreSQL 16
- Redis 7
- Persistent volumes for PostgreSQL and Redis
- Health checks for PostgreSQL and Redis

## Required configuration

Copy the example environment file and replace all placeholder values before deployment:

```bash
cp env.production.example .env.production
```

Required production values include:

- `APP_ENV=production`
- `DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `JWT_SECRET` / JWT secret setting used by the API
- SMTP provider values
- S3 provider values if using S3 storage

Do not commit `.env.production` or real secrets.

## Start the stack

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

## Check containers

```bash
docker compose -f docker-compose.prod.yml ps
```

## Check API health

```bash
curl http://localhost:8000/health
```

Expected response includes:

```json
{
  "status": "ok",
  "service": "prepared-api"
}
```

## Worker logs

```bash
docker compose -f docker-compose.prod.yml logs -f worker
```

## API logs

```bash
docker compose -f docker-compose.prod.yml logs -f api
```

## Stop the stack

```bash
docker compose -f docker-compose.prod.yml down
```

## Notes

- This deployment is suitable for a controlled VPS or internal staging environment.
- For public production, place the API behind a reverse proxy such as Nginx or a managed load balancer.
- Use managed PostgreSQL, managed Redis, and managed object storage for serious production deployments.
- Run legal, security, and infrastructure review before processing confidential customer data.
