from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from .hal_memory import read_hal_memory


@dataclass(frozen=True)
class HALProviderLearningSummary:
    provider: str
    observations: int
    dominant_mode: str
    safe_observations: int
    persistence_warnings: int
    confidence: float
    recommendation: str


def summarize_provider(provider: str, records: list[dict]) -> HALProviderLearningSummary:
    mode_counts: dict[str, int] = defaultdict(int)
    safe_observations = 0
    persistence_warnings = 0

    for record in records:
        mode_counts[str(record.get('mode', 'unknown'))] += 1
        if record.get('safe_for_real_customer_data') is True:
            safe_observations += 1
        if record.get('persistence_warning') is True:
            persistence_warnings += 1

    observations = len(records)
    dominant_mode = max(mode_counts.items(), key=lambda item: item[1])[0] if mode_counts else 'unknown'

    if observations == 0:
        confidence = 0.0
    else:
        stability_score = mode_counts.get(dominant_mode, 0) / observations
        safety_score = safe_observations / observations
        warning_penalty = persistence_warnings / observations
        confidence = max(0.0, min(1.0, (0.6 * stability_score) + (0.4 * safety_score) - (0.2 * warning_penalty)))

    if safe_observations == observations and observations > 0:
        recommendation = 'Provider profile appears production-capable based on stored HAL observations.'
    elif persistence_warnings > 0:
        recommendation = 'Provider profile is suitable for demo/MVP mode; add managed persistence before real customer data.'
    else:
        recommendation = 'Provider profile has limited observations; continue collecting HAL memory.'

    return HALProviderLearningSummary(
        provider=provider,
        observations=observations,
        dominant_mode=dominant_mode,
        safe_observations=safe_observations,
        persistence_warnings=persistence_warnings,
        confidence=round(confidence, 3),
        recommendation=recommendation,
    )


def build_hal_learning_summary(limit: int = 100) -> dict:
    records = read_hal_memory(limit=limit)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[str(record.get('provider', 'unknown'))].append(record)

    providers = [asdict(summarize_provider(provider, provider_records)) for provider, provider_records in sorted(grouped.items())]
    return {
        'observations': len(records),
        'providers': providers,
        'learning_status': 'insufficient-data' if len(records) < 3 else 'active',
    }
