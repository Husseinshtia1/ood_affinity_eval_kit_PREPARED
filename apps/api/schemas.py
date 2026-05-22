from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    DELETED = "DELETED"


class EvaluationSubmitResponse(BaseModel):
    status: JobStatus
    evaluation_id: str
    message: str


class EvaluationStatusResponse(BaseModel):
    evaluation_id: str
    status: JobStatus
    model_name: str | None = None
    detail: str | None = None
    report_available: bool = False


class EvaluationReportResponse(BaseModel):
    evaluation_id: str
    status: JobStatus = Field(default=JobStatus.COMPLETED)
    report: dict
