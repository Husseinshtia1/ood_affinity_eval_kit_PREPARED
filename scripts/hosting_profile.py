from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class HostingProfile:
    provider: str
    mode: str
    public_url: str | None
    has_database: bool
    has_redis: bool
    has_smtp: bool
    has_object_storage: bool


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


def build_profile() -> HostingProfile:
    database_url = os.getenv('DATABASE_URL', '')
    redis_url = os.getenv('REDIS_URL', '')
    smtp_host = os.getenv('SMTP_HOST', '')
    s3_bucket = os.getenv('S3_BUCKET', '')
    public_url = (
        os.getenv('RAILWAY_PUBLIC_DOMAIN')
        or os.getenv('RENDER_EXTERNAL_URL')
        or os.getenv('FLY_APP_NAME')
        or os.getenv('FRONTEND_URL')
    )

    has_database = bool(database_url and not database_url.startswith('sqlite'))
    has_redis = bool(redis_url and redis_url not in {'redis://redis:6379/0', 'redis://localhost:6379/0'})
    has_smtp = bool(smtp_host)
    has_object_storage = bool(s3_bucket)

    if has_database and has_redis:
        mode = 'production-ready'
    elif database_url.startswith('sqlite') or not database_url:
        mode = 'free-hosting-demo'
    else:
        mode = 'partial-managed'

    return HostingProfile(
        provider=detect_provider(),
        mode=mode,
        public_url=public_url,
        has_database=has_database,
        has_redis=has_redis,
        has_smtp=has_smtp,
        has_object_storage=has_object_storage,
    )


def main() -> None:
    profile = build_profile()
    print('[PREPARED] Hosting provider:', profile.provider)
    print('[PREPARED] Hosting mode:', profile.mode)
    print('[PREPARED] Public URL:', profile.public_url or 'not-detected')
    print('[PREPARED] Managed database:', 'yes' if profile.has_database else 'no')
    print('[PREPARED] Redis:', 'yes' if profile.has_redis else 'no')
    print('[PREPARED] SMTP:', 'yes' if profile.has_smtp else 'no')
    print('[PREPARED] Object storage:', 'yes' if profile.has_object_storage else 'no')


if __name__ == '__main__':
    main()
