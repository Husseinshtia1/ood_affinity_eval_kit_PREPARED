from __future__ import annotations

from dataclasses import asdict, dataclass

from .hosting_adaptation import detect_hosting_capabilities
from .hal_optimizer import build_runtime_optimization


@dataclass(frozen=True)
class HALContextFilterResult:
    provider: str
    profile: str
    active_rule_groups: list[str]
    suppressed_rule_groups: list[str]
    reason: str


def build_hal_context_filter_result() -> HALContextFilterResult:
    capabilities = detect_hosting_capabilities()
    optimization = build_runtime_optimization()

    active: list[str] = []
    suppressed: list[str] = []

    if optimization.profile == 'free-demo':
        active.extend([
            'sqlite-bootstrap-rules',
            'inline-task-rules',
            'temporary-storage-rules',
            'log-only-email-rules',
            'minimal-upload-limit-rules',
        ])
        suppressed.extend([
            'managed-postgres-rules',
            'redis-worker-rules',
            's3-persistent-storage-rules',
            'smtp-delivery-rules',
            'billing-production-rules',
        ])
        reason = 'Free-demo profile detected; HAL evaluates only lightweight hosting rules.'
    elif optimization.profile == 'production':
        active.extend([
            'managed-postgres-rules',
            'redis-worker-rules',
            's3-persistent-storage-rules',
            'smtp-delivery-rules',
            'monitoring-and-backup-rules',
        ])
        suppressed.extend([
            'sqlite-bootstrap-rules',
            'temporary-storage-rules',
            'log-only-email-rules',
        ])
        reason = 'Production profile detected; HAL evaluates managed infrastructure rules.'
    else:
        active.extend([
            'partial-managed-transition-rules',
            'database-gap-rules',
            'queue-gap-rules',
            'storage-gap-rules',
            'conservative-upload-limit-rules',
        ])
        suppressed.extend([
            'billing-production-rules',
            'full-autonomous-production-rules',
        ])
        reason = 'Partial-managed profile detected; HAL evaluates transition and gap-closure rules.'

    return HALContextFilterResult(
        provider=capabilities.provider,
        profile=optimization.profile,
        active_rule_groups=active,
        suppressed_rule_groups=suppressed,
        reason=reason,
    )


def hal_context_filter_dict() -> dict:
    return asdict(build_hal_context_filter_result())
