from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .hosting_adaptation import detect_hosting_capabilities
from .runtime_mutation import build_runtime_mutation_plan
from .settings import get_settings


@dataclass(frozen=True)
class HALMemoryRecord:
    timestamp: str
    provider: str
    mode: str
    database: str
    queue: str
    storage: str
    email: str
    task_execution: str
    database_mode: str
    storage_mode: str
    email_mode: str
    safe_for_real_customer_data: bool
    persistence_warning: bool


def hal_memory_path() -> Path:
    settings = get_settings()
    return settings.temp_storage_dir / 'hal_memory.jsonl'


def capture_hal_memory_record() -> HALMemoryRecord:
    capabilities = detect_hosting_capabilities()
    plan = build_runtime_mutation_plan()
    return HALMemoryRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider=capabilities.provider,
        mode=capabilities.mode,
        database=capabilities.database,
        queue=capabilities.queue,
        storage=capabilities.storage,
        email=capabilities.email,
        task_execution=plan.task_execution,
        database_mode=plan.database_mode,
        storage_mode=plan.storage_mode,
        email_mode=plan.email_mode,
        safe_for_real_customer_data=plan.safe_for_real_customer_data,
        persistence_warning=plan.persistence_warning,
    )


def append_hal_memory_record() -> dict:
    path = hal_memory_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = capture_hal_memory_record()
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(asdict(record), sort_keys=True) + '\n')
    return asdict(record)


def read_hal_memory(limit: int = 20) -> list[dict]:
    path = hal_memory_path()
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8').splitlines()[-limit:]
    records: list[dict] = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records
