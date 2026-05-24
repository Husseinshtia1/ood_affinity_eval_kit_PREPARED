from __future__ import annotations

from dataclasses import asdict, dataclass

from .hal_learning import build_hal_learning_summary
from .hal_optimizer import build_runtime_optimization
from .runtime_mutation import build_runtime_mutation_plan


@dataclass(frozen=True)
class HALAutonomyMetrics:
    hal_aix: float
    hal_icc: float
    hal_ttp: float
    autonomy_decisions: list[str]
    infrastructure_couplings: list[str]
    transition_notes: list[str]


def build_hal_autonomy_metrics() -> HALAutonomyMetrics:
    plan = build_runtime_mutation_plan()
    optimization = build_runtime_optimization()
    learning = build_hal_learning_summary(limit=100)

    autonomy_decisions: list[str] = []
    infrastructure_couplings: list[str] = []
    transition_notes: list[str] = []

    if plan.task_execution:
        autonomy_decisions.append('task_execution_mode')
        infrastructure_couplings.append('task_system')
    if optimization.max_upload_mb:
        autonomy_decisions.append('adaptive_upload_limit')
        infrastructure_couplings.append('request_ingestion')
    if plan.email_mode:
        autonomy_decisions.append('email_delivery_mode')
        infrastructure_couplings.append('notification_system')
    if plan.storage_mode:
        autonomy_decisions.append('storage_persistence_mode')
        infrastructure_couplings.append('artifact_storage')
    if plan.database_mode:
        autonomy_decisions.append('database_runtime_mode')
        infrastructure_couplings.append('data_persistence')
    if learning.get('learning_status') == 'active':
        autonomy_decisions.append('provider_learning_feedback')
        transition_notes.append('HAL learning has enough observations to start informing provider-specific behavior.')
    else:
        transition_notes.append('HAL learning is still collecting observations.')

    possible_decisions = 6
    possible_couplings = 5

    hal_aix = len(set(autonomy_decisions)) / possible_decisions
    hal_icc = len(set(infrastructure_couplings)) / possible_couplings

    safety_factor = 1.0 if plan.safe_for_real_customer_data else 0.55
    learning_factor = 1.0 if learning.get('learning_status') == 'active' else 0.65
    hal_ttp = ((hal_aix + hal_icc) / 2.0) * safety_factor * learning_factor

    if not plan.safe_for_real_customer_data:
        transition_notes.append('Current profile is not safe for real customer data; add PostgreSQL, Redis, and persistent object storage.')
    if optimization.profile == 'free-demo':
        transition_notes.append('Current profile is optimized for free/demo hosting.')

    return HALAutonomyMetrics(
        hal_aix=round(hal_aix, 3),
        hal_icc=round(hal_icc, 3),
        hal_ttp=round(hal_ttp, 3),
        autonomy_decisions=sorted(set(autonomy_decisions)),
        infrastructure_couplings=sorted(set(infrastructure_couplings)),
        transition_notes=transition_notes,
    )


def hal_autonomy_metrics_dict() -> dict:
    return asdict(build_hal_autonomy_metrics())
