# PREPARED.ai Free Hosting Mode

Free Hosting Mode is a lightweight deployment profile designed to make PREPARED.ai run on free or low-credit hosting platforms.

## Goal

Reduce the required infrastructure from a full SaaS stack:

- API
- Frontend
- Worker
- PostgreSQL
- Redis
- S3
- SMTP

Into a minimal free-hostable stack:

- API only, using local/ephemeral storage where necessary
- Frontend as a separate static/Next.js deployment
- No mandatory worker service
- No mandatory Redis
- No mandatory PostgreSQL for bootstrap
- No mandatory SMTP
- Optional managed services when available

## Recommended free-hosting architecture

```text
Frontend:
  Vercel / Cloudflare Pages / Netlify / Railway static container

API:
  Railway / Koyeb / Render / Fly.io / Zeabur using Dockerfile.api

Database:
  SQLite bootstrap mode or Supabase/Neon free PostgreSQL

Queue:
  Disabled in demo mode, or Redis only when available

Storage:
  Local temporary storage for demo, Cloudflare R2/Supabase Storage later

Email:
  Disabled by default, SMTP optional
```

## Minimal environment variables

```env
ENVIRONMENT=development
APP_NAME=PREPARED.ai API Gateway
APP_VERSION=0.1.0-p0
JWT_SECRET_KEY=replace-with-demo-secret
DATABASE_URL=sqlite:///./prepared.db
FRONTEND_URL=https://your-frontend-domain
SMTP_FROM_EMAIL=no-reply@example.com
TEMP_STORAGE_DIR=/tmp/prepared_jobs
MAX_UPLOAD_BYTES=26214400
REPORT_TTL_MINUTES=60
ALLOWED_ORIGINS=https://your-frontend-domain,http://localhost:3000
```

## What is intentionally disabled or simplified

- Production-grade database migrations are not required for initial boot.
- Celery worker can be skipped until Redis is available.
- SMTP is optional; invitations can be logged instead.
- Billing remains disabled.
- S3/object storage is optional.

## Upgrade path

Free Hosting Mode should be treated as an MVP/demo mode.

Upgrade path:

1. Add managed PostgreSQL.
2. Add Redis.
3. Add worker service.
4. Re-enable controlled migrations.
5. Add persistent object storage.
6. Add SMTP provider.
7. Add monitoring and legal/security review.

## Suitable platforms

This mode is suitable for:

- Railway free/credit tier
- Koyeb free/low-cost services
- Render free/low-cost services
- Fly.io small apps
- Vercel/Netlify/Cloudflare Pages for frontend
- Supabase or Neon for optional free PostgreSQL
- Upstash for optional Redis

## Important warnings

Free Hosting Mode is not intended for:

- Real customer data
- Confidential scientific data
- Enterprise production use
- Paid billing workflows
- Regulated or clinical decision-making

Use it for demos, investor previews, open-source trials, and public technical validation.
