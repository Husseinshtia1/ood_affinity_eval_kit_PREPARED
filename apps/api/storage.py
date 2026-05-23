from __future__ import annotations

import json
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException

from .schemas import JobStatus
from .settings import get_settings
from .storage_backends import LocalStorageBackend, S3StorageBackend, get_storage_backend

settings = get_settings()
GENERATED_FILES = ("metadata.json", "report.json", "parity_points.json")


def require_local_backend() -> LocalStorageBackend:
    backend = get_storage_backend()
    if not isinstance(backend, LocalStorageBackend):
        raise HTTPException(status_code=501, detail="This storage operation is not yet implemented for non-local backends")
    return backend


def local_fallback_dir(job_id: str) -> Path:
    path = settings.temp_storage_dir / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def local_object_path(job_id: str, filename: str) -> Path:
    backend = get_storage_backend()
    if isinstance(backend, LocalStorageBackend):
        return backend.object_path(job_id, filename)
    return local_fallback_dir(job_id) / filename


def sync_to_remote_if_needed(job_id: str, filename: str, local_path: Path) -> None:
    backend = get_storage_backend()
    if isinstance(backend, S3StorageBackend):
        backend.upload_file(local_path, job_id, filename)


def job_dir(job_id: str) -> Path:
    return require_local_backend().job_dir(job_id)


def predictions_path(job_id: str) -> Path:
    return local_object_path(job_id, "predictions.csv")


def report_path(job_id: str) -> Path:
    return local_object_path(job_id, "report.json")


def points_path(job_id: str) -> Path:
    return local_object_path(job_id, "parity_points.json")


def metadata_path(job_id: str) -> Path:
    return local_object_path(job_id, "metadata.json")


def write_metadata(job_id: str, payload: dict) -> None:
    path = metadata_path(job_id)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    sync_to_remote_if_needed(job_id, "metadata.json", path)


def read_metadata(job_id: str) -> dict:
    path = metadata_path(job_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Evaluation job not found")
    return json.loads(path.read_text(encoding="utf-8"))


def sync_generated_files(job_id: str) -> None:
    for filename in GENERATED_FILES:
        path = local_object_path(job_id, filename)
        if path.exists():
            sync_to_remote_if_needed(job_id, filename, path)


def update_status(job_id: str, status: JobStatus, detail: str | None = None) -> None:
    metadata = read_metadata(job_id)
    metadata["status"] = status.value
    if detail:
        metadata["detail"] = detail
    write_metadata(job_id, metadata)


async def save_upload(job_id: str, upload: UploadFile) -> Path:
    if not upload.filename or not upload.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV prediction files are accepted")

    target = predictions_path(job_id)
    total = 0
    with target.open("wb") as buffer:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > settings.max_upload_bytes:
                raise HTTPException(status_code=413, detail="Uploaded file exceeds maximum allowed size")
            buffer.write(chunk)

    sync_to_remote_if_needed(job_id, "predictions.csv", target)
    return target


def delete_job(job_id: str) -> None:
    backend = get_storage_backend()
    if isinstance(backend, S3StorageBackend):
        for filename in ("predictions.csv",) + GENERATED_FILES:
            backend.delete_object(job_id, filename)

    path = settings.temp_storage_dir / job_id
    if path.exists():
        shutil.rmtree(path)
