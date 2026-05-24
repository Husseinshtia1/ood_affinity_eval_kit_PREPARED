from __future__ import annotations

from dataclasses import asdict, dataclass

from .runtime_mutation import build_runtime_mutation_plan


@dataclass(frozen=True)
class HALComplexityDecision:
    selected_path: str
    complexity_score: float
    escalation_allowed: bool
    escalation_reason: str | None
    suppressed_escalations: list[str]


def build_hal_complexity_decision() -> HALComplexityDecision:
    """Prefer the simplest sufficient hosting/runtime path.

    This mirrors the idea of avoiding over-reasoning: if a simpler execution
    path is sufficient for the current deployment profile, HAL should not
    escalate to heavier infrastructure automatically.
    """

    plan = build_runtime_mutation_plan()
    suppressed: list[str] = []

    if plan.safe_for_real_customer_data:
        return HALComplexityDecision(
            selected_path='production-managed-stack',
            complexity_score=1.0,
            escalation_allowed=True,
            escalation_reason='Managed PostgreSQL, Redis worker execution, and persistent storage are available.',
            suppressed_escalations=[],
        )

    if plan.task_execution == 'inline-or-disabled' and plan.database_mode in {'sqlite-demo', 'ephemeral-bootstrap'}:
        suppressed.extend([
            'do-not-require-redis-worker-for-demo',
            'do-not-require-managed-postgresql-for-bootstrap',
            'do-not-require-s3-for-temporary-reports',
        ])
        return HALComplexityDecision(
            selected_path='minimal-free-hosting-path',
            complexity_score=0.25,
            escalation_allowed=False,
            escalation_reason=None,
            suppressed_escalations=suppressed,
        )

    if plan.persistence_warning:
        suppressed.append('delay-full-production-escalation-until-persistence-is-configured')
        return HALComplexityDecision(
            selected_path='partial-managed-path',
            complexity_score=0.55,
            escalation_allowed=True,
            escalation_reason='Some managed services are present, but persistence is incomplete.',
            suppressed_escalations=suppressed,
        )

    return HALComplexityDecision(
        selected_path='unknown-conservative-path',
        complexity_score=0.5,
        escalation_allowed=False,
        escalation_reason=None,
        suppressed_escalations=['hold-escalation-until-more-signals-are-available'],
    )


def hal_complexity_decision_dict() -> dict:
    return asdict(build_hal_complexity_decision())
