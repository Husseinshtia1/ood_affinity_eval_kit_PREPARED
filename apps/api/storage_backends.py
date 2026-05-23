from __future__ import annotations

from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

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
        self._client = None

    def require_configured(self) -> None:
        if not self.bucket or not self.region:
            raise HTTPException(status_code=500, detail='S3 storage is selected but S3 bucket or region is not configured')

    @property
    def client(self):
        self.require_configured()
        if self._client is None:
            self._client = boto3.client('s3', region_name=self.region)
        return self._client

    def object_key(self, job_id: str, filename: str) -> str:
        self.require_configured()
        return f'{self.prefix}/{job_id}/{filename}'

    def upload_file(self, local_path: Path, job_id: str, filename: str) -> str:
        key = self.object_key(job_id, filename)
        try:
            self.client.upload_file(str(local_path), self.bucket, key)
            return key
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(status_code=502, detail=f'S3 upload failed: {exc}') from exc

    def download_file(self, job_id: str, filename: str, local_path: Path) -> Path:
        key = self.object_key(job_id, filename)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.client.download_file(self.bucket, key, str(local_path))
            return local_path
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(status_code=502, detail=f'S3 download failed: {exc}') from exc

    def delete_object(self, job_id: str, filename: str) -> None:
        key = self.object_key(job_id, filename)
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(status_code=502, detail=f'S3 delete failed: {exc}') from exc

    def presigned_url(self, job_id: str, filename: str, expires_in: int = 900) -> str:
        key = self.object_key(job_id, filename)
        try:
            return self.client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expires_in,
            )
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(status_code=502, detail=f'S3 presigned URL failed: {exc}') from exc


def get_storage_backend():
    settings = get_settings()
    if settings.storage_backend == 'local':
        return LocalStorageBackend(settings.temp_storage_dir)
    if settings.storage_backend == 's3':
        return S3StorageBackend(settings.s3_bucket, settings.s3_region, settings.s3_prefix)
    raise RuntimeError(f'Unsupported storage backend: {settings.storage_backend}')
