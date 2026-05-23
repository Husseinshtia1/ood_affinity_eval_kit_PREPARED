from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, UploadFile

from .settings import get_settings


class LocalStorageBackend:
    def __init__(self, root: Path):
        self.root = root

    def job_dir(self, job_id: str) -> Path:
        path = self.root / job_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def object_path(self, job_id: str, filename: str) -> Path:
        return self.job_dir(job_id) / filename


class S3StorageBackend:
    def __init__(self, bucket: str | None, region: str | None, prefix: str):
        self.bucket = bucket
        self.region = region
        self.prefix = prefix.strip('/')

    def require_configured(self) -> None:
        if not self.bucket or not self.region:
            raise HTTPException(status_code=500, detail='S3 storage is selected but S3 bucket or region is not configured')

    def object_key(self, job_id: str, filename: str) -> str:
        self.require_configured()
        return f'{self.prefix}/{job_id}/{filename}'


def get_storage_backend():
    settings = get_settings()
    if settings.storage_backend == 'local':
        return LocalStorageBackend(settings.temp_storage_dir)
    if settings.storage_backend == 's3':
        return S3StorageBackend(settings.s3_bucket, settings.s3_region, settings.s3_prefix)
    raise RuntimeError(f'Unsupported storage backend: {settings.storage_backend}')
