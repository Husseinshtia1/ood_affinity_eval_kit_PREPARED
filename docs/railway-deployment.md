# PREPARED.ai Railway Deployment Plan

Railway can be used as an MVP/staging deployment target for PREPARED.ai.

## Recommended Railway services

Create separate Railway services for:

1. `prepared-api`
   - Source: this GitHub repository
   - Dockerfile: `Dockerfile.api`
   - Public networking: enabled
   - Health check path: `/health`

2. `prepared-worker`
   - Source: this GitHub repository
   - Dockerfile: `Dockerfile.worker`
   - Public networking: disabled

3. PostgreSQL
   - Railway managed PostgreSQL plugin/service

4. Redis
   - Railway managed Redis plugin/service, if available
   - Alternative: external Redis provider such as Upstash

## Required environment variables

Set these variables on the API and worker services as appropriate:

```env
APP_ENV=production
ENVIRONMENT=production
FRONTEND_URL=https://your-frontend-domain
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
JWT_SECRET_KEY=replace-with-railway-secret
SMTP_HOST=replace-with-provider-host
SMTP_PORT=587
SMTP_USERNAME=replace-with-provider-user
SMTP_PASSWORD=replace-with-provider-password
SMTP_FROM_EMAIL=no-reply@prepared.ai
STORAGE_BACKEND=local
RATE_LIMIT_ENABLED=true
```

For S3/R2 storage later:

```env
STORAGE_BACKEND=s3
S3_BUCKET=replace-me
S3_REGION=auto-or-region
AWS_ACCESS_KEY_ID=replace-me
AWS_SECRET_ACCESS_KEY=replace-me
```

## API service settings

- Build: Dockerfile
- Dockerfile path: `Dockerfile.api`
- Start command: use Dockerfile default
- Health check path: `/health`

## Worker service settings

- Build: Dockerfile
- Dockerfile path: `Dockerfile.worker`
- Start command: use Dockerfile default
- Public domain: disabled

## Frontend

Recommended frontend host:

- Vercel for `frontend/prepared-web`

Set:

```env
NEXT_PUBLIC_API_URL=https://your-railway-api-domain
```

Alternative:
- Deploy the frontend as a separate Railway service if desired, but Vercel is simpler for Next.js.

## Deployment order

1. Create PostgreSQL service.
2. Create Redis service or connect Upstash.
3. Create `prepared-api` service from GitHub.
4. Create `prepared-worker` service from GitHub.
5. Add all production environment variables.
6. Deploy API and verify `/health`.
7. Deploy worker and verify Celery logs.
8. Deploy frontend and set `NEXT_PUBLIC_API_URL`.

## Verification

```bash
curl https://your-railway-api-domain/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "prepared-api"
}
```

## Important limitations

- Railway free/credit limits may change; verify current pricing before relying on it.
- Do not store real production secrets in GitHub.
- Use Railway environment variables/secrets.
- Billing remains disabled until payment provider/legal review is complete.
- Live customer data should not be processed until security/legal review is complete.
