from __future__ import annotations

from dataclasses import asdict, dataclass

from .hal_learning import build_hal_learning_summary
from .runtime_mutation import build_runtime_mutation_plan


@dataclass(frozen=True)
class HALRuntimeOptimization:
    profile: str
    max_upload_mb: int
    task_mode: str
    cache_policy: str
    persistence_policy: str
    customer_data_policy: str
    recommended_next_step: str
    rationale: list[str]


def build_runtime_optimization() -> HALRuntimeOptimization:
    plan = build_runtime_mutation_plan()
    learning = build_hal_learning_summary(limit=100)
    rationale: list[str] = []

    if plan.safe_for_real_customer_data:
        profile = 'production'
        max_upload_mb = 25
        cache_policy = 'standard'
        persistence_policy = 'persistent'
        customer_data_policy = 'allowed-after-legal-review'
        recommended_next_step = 'Enable monitoring, backups, and controlled migrations.'
        rationale.append('PostgreSQL, persistent storage, and worker execution are available.')
    elif plan.persistence_warning:
        profile = 'free-demo'
        max_upload_mb = 5
        cache_policy = 'minimal-memory'
        persistence_policy = 'ephemeral'
        customer_data_policy = 'synthetic-or-demo-only'
        recommended_next_step = 'Add managed PostgreSQL, Redis, and object storage before real usage.'
        rationale.append('Persistence warning detected by HAL mutation plan.')
    else:
        profile = 'partial-managed'
        max_upload_mb = 10
        cache_policy = 'conservative'
        persistence_policy = 'partial'
        customer_data_policy = 'internal-testing-only'
        recommended_next_step = 'Complete missing managed services before production launch.'
        rationale.append('Some managed services are available, but the profile is not fully production-safe.')

    if plan.task_execution != 'celery-worker':
        rationale.append('Celery worker is not available; using inline or disabled task mode.')

    if learning.get('learning_status') == 'insufficient-data':
        rationale.append('HAL learning has insufficient observations; continue capturing memory records.')
    else:
        rationale.append('HAL learning summary is active and can inform future provider-specific optimization.')

    return HALRuntimeOptimization(
        profile=profile,
        max_upload_mb=max_upload_mb,
        task_mode=plan.task_execution,
        cache_policy=cache_policy,
        persistence_policy=persistence_policy,
        customer_data_policy=customer_data_policy,
        recommended_next_step=recommended_next_step,
        rationale=rationale,
    )


def runtime_optimization_dict() -> dict:
    return asdict(build_runtime_optimization())
