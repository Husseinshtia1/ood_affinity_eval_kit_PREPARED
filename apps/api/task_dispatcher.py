from __future__ import annotations

from pathlib import Path

from .runtime_mutation import build_runtime_mutation_plan


def dispatch_evaluation(job_id: str, predictions_path: str) -> dict:
    """Dispatch an evaluation according to the HAL runtime mutation plan.

    In production-ready mode this uses Celery. In free-hosting/demo mode it runs
    inline so the app can work without Redis or a separate worker service.
    """

    plan = build_runtime_mutation_plan()

    if plan.task_execution == 'celery-worker':
        from worker.tasks import evaluate_job

        evaluate_job.delay(job_id, predictions_path)
        return {'dispatched': True, 'mode': 'celery-worker'}

    from worker.tasks import evaluate_job

    evaluate_job(job_id, str(Path(predictions_path)))
    return {'dispatched': True, 'mode': 'inline'}


def dispatch_invitation_email(invitation_id: int) -> dict:
    """Dispatch invitation delivery according to HAL runtime capabilities."""

    plan = build_runtime_mutation_plan()

    if plan.task_execution == 'celery-worker':
        from worker.tasks import send_invitation_email_task

        send_invitation_email_task.delay(invitation_id)
        return {'dispatched': True, 'mode': 'celery-worker'}

    from worker.tasks import send_invitation_email_task

    send_invitation_email_task(invitation_id)
    return {'dispatched': True, 'mode': 'inline'}
