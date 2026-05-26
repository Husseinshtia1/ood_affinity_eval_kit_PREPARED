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
    active_rule_groups: list[str]
    suppressed_rule_groups: list[str]
    rationale: list[str]


def infer_rule_groups(profile: str) -> tuple[list[str], list[str]]:
    if profile == 'free-demo':
        return (
            [
                'sqlite-bootstrap-rules',
                'inline-task-rules',
                'temporary-storage-rules',
                'log-only-email-rules',
                'minimal-upload-limit-rules',
            ],
            [
                'managed-postgres-rules',
                'redis-worker-rules',
                's3-persistent-storage-rules',
                'smtp-delivery-rules',
                'billing-production-rules',
            ],
        )
    if profile == 'production':
        return (
            [
                'managed-postgres-rules',
                'redis-worker-rules',
                's3-persistent-storage-rules',
                'smtp-delivery-rules',
                'monitoring-and-backup-rules',
            ],
            [
                'sqlite-bootstrap-rules',
                'temporary-storage-rules',
                'log-only-email-rules',
            ],
        )
    return (
        [
            'partial-managed-transition-rules',
            'database-gap-rules',
            'queue-gap-rules',
            'storage-gap-rules',
            'conservative-upload-limit-rules',
        ],
        [
            'billing-production-rules',
            'full-autonomous-production-rules',
        ],
    )


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

    active_rule_groups, suppressed_rule_groups = infer_rule_groups(profile)

    if 'minimal-upload-limit-rules' in active_rule_groups:
        max_upload_mb = min(max_upload_mb, 5)
        rationale.append('Context filter activated minimal upload limits for free/demo hosting.')
    if 'conservative-upload-limit-rules' in active_rule_groups:
        max_upload_mb = min(max_upload_mb, 10)
        rationale.append('Context filter activated conservative upload limits for partial-managed hosting.')
    if 'inline-task-rules' in active_rule_groups and plan.task_execution != 'celery-worker':
        rationale.append('Context filter prefers inline or disabled task execution for lightweight hosting.')

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
        active_rule_groups=active_rule_groups,
        suppressed_rule_groups=suppressed_rule_groups,
        rationale=rationale,
    )


def runtime_optimization_dict() -> dict:
    return asdict(build_runtime_optimization())
