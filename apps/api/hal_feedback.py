from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from .hal_outcomes import read_hal_outcomes


@dataclass(frozen=True)
class HALPathFeedback:
    selected_path: str
    observations: int
    successes: int
    failures: int
    success_rate: float
    average_duration_ms: float | None
    confidence: float
    recommendation: str


def summarize_path(selected_path: str, records: list[dict]) -> HALPathFeedback:
    observations = len(records)
    successes = sum(1 for item in records if item.get('success') is True)
    failures = observations - successes
    durations = [item.get('duration_ms') for item in records if isinstance(item.get('duration_ms'), int)]
    average_duration_ms = round(sum(durations) / len(durations), 2) if durations else None
    success_rate = successes / observations if observations else 0.0

    sample_factor = min(1.0, observations / 10.0)
    duration_penalty = 0.0
    if average_duration_ms is not None and average_duration_ms > 5000:
        duration_penalty = 0.15
    confidence = max(0.0, min(1.0, (success_rate * 0.8 + sample_factor * 0.2) - duration_penalty))

    if observations < 3:
        recommendation = 'Insufficient evidence; continue collecting outcomes.'
    elif success_rate >= 0.9:
        recommendation = 'Path is reliable for the current hosting profile.'
    elif success_rate >= 0.6:
        recommendation = 'Path is usable but should remain monitored.'
    else:
        recommendation = 'Path is unstable; consider escalation or alternate runtime mode.'

    return HALPathFeedback(
        selected_path=selected_path,
        observations=observations,
        successes=successes,
        failures=failures,
        success_rate=round(success_rate, 3),
        average_duration_ms=average_duration_ms,
        confidence=round(confidence, 3),
        recommendation=recommendation,
    )


def build_hal_feedback_summary(limit: int = 200) -> dict:
    records = read_hal_outcomes(limit=limit)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[str(record.get('selected_path', 'unknown'))].append(record)

    paths = [asdict(summarize_path(path, items)) for path, items in sorted(grouped.items())]
    return {
        'observations': len(records),
        'feedback_status': 'insufficient-data' if len(records) < 3 else 'active',
        'paths': paths,
    }
