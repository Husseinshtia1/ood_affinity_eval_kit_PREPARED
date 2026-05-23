from pathlib import Path

from worker.celery_app import celery_app
from apps.api.prepared_runner import run_prepared_evaluation
from apps.api.settings import get_settings
from apps.api.schemas import JobStatus
from apps.api.storage import report_path, points_path, update_status
from apps.api.database import SessionLocal
from apps.api.models import Evaluation

settings = get_settings()


def update_db_status(job_id: str, status: JobStatus) -> None:
    with SessionLocal() as db:
        evaluation = db.query(Evaluation).filter(Evaluation.job_id == job_id).first()
        if evaluation:
            evaluation.status = status.value
            db.commit()


@celery_app.task(name="prepared.evaluate")
def evaluate_job(job_id: str, predictions_path: str):
    try:
        update_status(job_id, JobStatus.VALIDATING, "Prediction file accepted; starting validation.")
        update_db_status(job_id, JobStatus.VALIDATING)

        update_status(job_id, JobStatus.RUNNING, "PREPARED evaluation engine is running.")
        update_db_status(job_id, JobStatus.RUNNING)

        report = run_prepared_evaluation(
            repo_root=settings.repo_root,
            predictions_csv=Path(predictions_path),
            report_path=report_path(job_id),
            points_path=points_path(job_id),
        )

        update_status(job_id, JobStatus.COMPLETED, "Evaluation completed successfully.")
        update_db_status(job_id, JobStatus.COMPLETED)
        return report

    except Exception as exc:
        update_status(job_id, JobStatus.FAILED, str(exc))
        update_db_status(job_id, JobStatus.FAILED)
        raise
