from __future__ import annotations

import json
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException

from .schemas import JobStatus
from .settings import get_settings

settings = get_settings()


def job_dir(job_id: str) -> Path:
    path = settings.temp_storage_dir / job_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def predictions_path(job_id: str) -> Path:
    return job_dir(job_id) / "predictions.csv"


def report_path(job_id: str) -> Path:
    return job_dir(job_id) / "report.json"


def points_path(job_id: str) -> Path:
    return job_dir(job_id) / "parity_points.json"


def metadata_path(job_id: str) -> Path:
    return job_dir(job_id) / "metadata.json"


def write_metadata(job_id: str, payload: dict) -> None:
    metadata_path(job_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_metadata(job_id: str) -> dict:
    path = metadata_path(job_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Evaluation job not found")
    return json.loads(path.read_text(encoding="utf-8"))


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
    return target


def delete_job(job_id: str) -> None:
    path = settings.temp_storage_dir / job_id
    if path.exists():
        shutil.rmtree(path)
