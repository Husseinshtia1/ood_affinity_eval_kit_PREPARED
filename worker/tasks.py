from pathlib import Path

from worker.celery_app import celery_app
from apps.api.prepared_runner import run_prepared_evaluation
from apps.api.settings import get_settings
from apps.api.schemas import JobStatus
from apps.api.storage import report_path, points_path, update_status

settings = get_settings()


@celery_app.task(name="prepared.evaluate")
def evaluate_job(job_id: str, predictions_path: str):
    try:
        update_status(job_id, JobStatus.VALIDATING, "Prediction file accepted; starting validation.")
        update_status(job_id, JobStatus.RUNNING, "PREPARED evaluation engine is running.")

        report = run_prepared_evaluation(
            repo_root=settings.repo_root,
            predictions_csv=Path(predictions_path),
            report_path=report_path(job_id),
            points_path=points_path(job_id),
        )

        update_status(job_id, JobStatus.COMPLETED, "Evaluation completed successfully.")
        return report

    except Exception as exc:
        update_status(job_id, JobStatus.FAILED, str(exc))
        raise
