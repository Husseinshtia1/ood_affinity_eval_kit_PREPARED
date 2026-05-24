from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .hal_complexity import build_hal_complexity_decision
from .runtime_mutation import build_runtime_mutation_plan
from .settings import get_settings


@dataclass(frozen=True)
class HALOutcomeRecord:
    timestamp: str
    operation: str
    success: bool
    duration_ms: int | None
    selected_path: str
    task_execution: str
    database_mode: str
    storage_mode: str
    email_mode: str
    error: str | None
    metadata: dict[str, Any]


def hal_outcomes_path() -> Path:
    settings = get_settings()
    path = settings.temp_storage_dir / 'hal_outcomes.jsonl'
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def record_hal_outcome(
    operation: str,
    success: bool,
    duration_ms: int | None = None,
    error: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    complexity = build_hal_complexity_decision()
    mutation = build_runtime_mutation_plan()
    record = HALOutcomeRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        operation=operation,
        success=success,
        duration_ms=duration_ms,
        selected_path=complexity.selected_path,
        task_execution=mutation.task_execution,
        database_mode=mutation.database_mode,
        storage_mode=mutation.storage_mode,
        email_mode=mutation.email_mode,
        error=error[:500] if error else None,
        metadata=metadata or {},
    )
    path = hal_outcomes_path()
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(asdict(record), sort_keys=True) + '\n')
    return asdict(record)


def read_hal_outcomes(limit: int = 50) -> list[dict]:
    path = hal_outcomes_path()
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding='utf-8').splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows
