from __future__ import annotations

from fastapi import HTTPException, UploadFile

from .hal_optimizer import build_runtime_optimization
from .settings import get_settings


def effective_max_upload_bytes() -> int:
    settings = get_settings()
    optimization = build_runtime_optimization()
    hal_limit = optimization.max_upload_mb * 1024 * 1024
    return min(settings.max_upload_bytes, hal_limit)


async def enforce_upload_limit(file: UploadFile) -> None:
    max_bytes = effective_max_upload_bytes()
    size = getattr(file, 'size', None)
    if size is not None and size > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f'Upload exceeds adaptive HAL limit of {max_bytes} bytes.',
        )
