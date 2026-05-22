from pathlib import Path
from worker.celery_app import celery_app
from apps.api.prepared_runner import run_prepared_evaluation
from apps.api.settings import get_settings

settings=get_settings()

@celery_app.task(name='prepared.evaluate')
def evaluate_job(job_id:str,predictions_path:str):

    report_path=settings.temp_storage_dir / f'{job_id}_report.json'

    return run_prepared_evaluation(
        repo_root=settings.repo_root,
        predictions_csv=Path(predictions_path),
        report_path=report_path
    )