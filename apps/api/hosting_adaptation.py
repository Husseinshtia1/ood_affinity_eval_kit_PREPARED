from __future__ import annotations

import os
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class HostingCapabilities:
    provider: str
    mode: str
    database: str
    queue: str
    storage: str
    email: str
    public_url: str | None
    recommendations: list[str]


def detect_provider() -> str:
    if os.getenv('RAILWAY_PROJECT_ID') or os.getenv('RAILWAY_SERVICE_ID'):
        return 'railway'
    if os.getenv('RENDER') or os.getenv('RENDER_SERVICE_ID'):
        return 'render'
    if os.getenv('FLY_APP_NAME'):
        return 'flyio'
    if os.getenv('KOYEB_APP_NAME') or os.getenv('KOYEB_SERVICE_NAME'):
        return 'koyeb'
    if os.getenv('VERCEL'):
        return 'vercel'
    if os.getenv('DIGITALOCEAN_APP_ID') or os.getenv('APP_PLATFORM'):
        return 'digitalocean'
    if os.getenv('CODESPACES'):
        return 'github-codespaces'
    return 'generic'


def infer_database() -> str:
    database_url = os.getenv('DATABASE_URL', '')
    if database_url.startswith('postgres'):
        return 'postgresql'
    if database_url.startswith('sqlite'):
        return 'sqlite'
    if database_url:
        return 'custom'
    return 'ephemeral-sqlite-recommended'


def infer_queue() -> str:
    redis_url = os.getenv('REDIS_URL', '')
    if redis_url and redis_url not in {'redis://redis:6379/0', 'redis://localhost:6379/0'}:
        return 'redis'
    return 'inline-or-disabled'


def infer_storage() -> str:
    if os.getenv('S3_BUCKET'):
        return 's3-compatible'
    return 'local-temp'


def infer_email() -> str:
    if os.getenv('SMTP_HOST'):
        return 'smtp'
    return 'disabled-log-only'


def infer_public_url() -> str | None:
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if railway_domain:
        return f'https://{railway_domain}'
    return os.getenv('RENDER_EXTERNAL_URL') or os.getenv('FRONTEND_URL')


def build_recommendations(database: str, queue: str, storage: str, email: str) -> list[str]:
    recommendations: list[str] = []
    if database != 'postgresql':
        recommendations.append('Use SQLite only for demo/free-hosting mode; add managed PostgreSQL before real customer data.')
    if queue != 'redis':
        recommendations.append('Run evaluations inline or disabled in free mode; add Redis before enabling Celery worker workflows.')
    if storage == 'local-temp':
        recommendations.append('Local temp storage is ephemeral; add S3/R2/Supabase Storage before persistent reports.')
    if email != 'smtp':
        recommendations.append('SMTP is disabled; invitations should be logged or queued until provider credentials are configured.')
    if not recommendations:
        recommendations.append('Hosting profile looks production-ready; verify migrations, monitoring, backups, and legal/security review.')
    return recommendations


def detect_hosting_capabilities() -> HostingCapabilities:
    database = infer_database()
    queue = infer_queue()
    storage = infer_storage()
    email = infer_email()

    production_ready = database == 'postgresql' and queue == 'redis' and storage == 's3-compatible' and email == 'smtp'
    partial = database == 'postgresql' or queue == 'redis'
    mode = 'production-ready' if production_ready else 'partial-managed' if partial else 'free-hosting-demo'

    return HostingCapabilities(
        provider=detect_provider(),
        mode=mode,
        database=database,
        queue=queue,
        storage=storage,
        email=email,
        public_url=infer_public_url(),
        recommendations=build_recommendations(database, queue, storage, email),
    )


def hosting_capabilities_dict() -> dict:
    return asdict(detect_hosting_capabilities())
