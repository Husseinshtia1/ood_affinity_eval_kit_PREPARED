from __future__ import annotations

import time
from pathlib import Path

from .hal_outcomes import record_hal_outcome
from .hal_reweighting import build_hal_decision_reweighting
from .runtime_mutation import build_runtime_mutation_plan


def should_use_celery() -> tuple[bool, dict]:
    plan = build_runtime_mutation_plan()
    reweighting = build_hal_decision_reweighting()

    if plan.task_execution != 'celery-worker':
        return False, {
            'reason': 'mutation-plan-does-not-enable-celery',
            'reweighting': reweighting.decision,
            'confidence': reweighting.path_confidence,
        }

    if reweighting.should_escalate is False and reweighting.decision in {'stabilize-current-path', 'collect-more-evidence', 'insufficient-data', 'monitor-current-path'}:
        return True, {
            'reason': 'celery-enabled-and-current-path-accepted',
            'reweighting': reweighting.decision,
            'confidence': reweighting.path_confidence,
        }

    return False, {
        'reason': 'decision-reweighting-blocked-celery-escalation',
        'reweighting': reweighting.decision,
        'confidence': reweighting.path_confidence,
    }


def dispatch_evaluation(job_id: str, predictions_path: str) -> dict:
    """Dispatch an evaluation according to HAL mutation and feedback decisions."""

    start = time.perf_counter()
    use_celery, decision = should_use_celery()
    mode = 'celery-worker' if use_celery else 'inline'

    try:
        if use_celery:
            from worker.tasks import evaluate_job

            evaluate_job.delay(job_id, predictions_path)
        else:
            from worker.tasks import evaluate_job

            evaluate_job(job_id, str(Path(predictions_path)))

        duration_ms = int((time.perf_counter() - start) * 1000)
        outcome = record_hal_outcome(
            operation='evaluation_dispatch',
            success=True,
            duration_ms=duration_ms,
            metadata={'job_id': job_id, 'mode': mode, 'decision': decision},
        )
        return {'dispatched': True, 'mode': mode, 'hal_decision': decision, 'hal_outcome': outcome}
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        record_hal_outcome(
            operation='evaluation_dispatch',
            success=False,
            duration_ms=duration_ms,
            error=str(exc),
            metadata={'job_id': job_id, 'mode': mode, 'decision': decision},
        )
        raise


def dispatch_invitation_email(invitation_id: int) -> dict:
    """Dispatch invitation delivery according to HAL mutation and feedback decisions."""

    start = time.perf_counter()
    use_celery, decision = should_use_celery()
    mode = 'celery-worker' if use_celery else 'inline'

    try:
        if use_celery:
            from worker.tasks import send_invitation_email_task

            send_invitation_email_task.delay(invitation_id)
        else:
            from worker.tasks import send_invitation_email_task

            send_invitation_email_task(invitation_id)

        duration_ms = int((time.perf_counter() - start) * 1000)
        outcome = record_hal_outcome(
            operation='invitation_dispatch',
            success=True,
            duration_ms=duration_ms,
            metadata={'invitation_id': invitation_id, 'mode': mode, 'decision': decision},
        )
        return {'dispatched': True, 'mode': mode, 'hal_decision': decision, 'hal_outcome': outcome}
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start) * 1000)
        record_hal_outcome(
            operation='invitation_dispatch',
            success=False,
            duration_ms=duration_ms,
            error=str(exc),
            metadata={'invitation_id': invitation_id, 'mode': mode, 'decision': decision},
        )
        raise
