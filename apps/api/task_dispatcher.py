from __future__ import annotations

from pathlib import Path

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

    use_celery, decision = should_use_celery()

    if use_celery:
        from worker.tasks import evaluate_job

        evaluate_job.delay(job_id, predictions_path)
        return {'dispatched': True, 'mode': 'celery-worker', 'hal_decision': decision}

    from worker.tasks import evaluate_job

    evaluate_job(job_id, str(Path(predictions_path)))
    return {'dispatched': True, 'mode': 'inline', 'hal_decision': decision}


def dispatch_invitation_email(invitation_id: int) -> dict:
    """Dispatch invitation delivery according to HAL mutation and feedback decisions."""

    use_celery, decision = should_use_celery()

    if use_celery:
        from worker.tasks import send_invitation_email_task

        send_invitation_email_task.delay(invitation_id)
        return {'dispatched': True, 'mode': 'celery-worker', 'hal_decision': decision}

    from worker.tasks import send_invitation_email_task

    send_invitation_email_task(invitation_id)
    return {'dispatched': True, 'mode': 'inline', 'hal_decision': decision}
