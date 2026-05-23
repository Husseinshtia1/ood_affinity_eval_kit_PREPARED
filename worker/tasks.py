from pathlib import Path

from worker.celery_app import celery_app
from apps.api.prepared_runner import run_prepared_evaluation
from apps.api.settings import get_settings
from apps.api.schemas import JobStatus
from apps.api.storage import report_path, points_path, update_status
from apps.api.database import SessionLocal
from apps.api.models import Evaluation, AuditLog, Invitation
from apps.api.notifications import send_invitation_email

settings = get_settings()


def update_db_status(job_id: str, status: JobStatus, detail: str | None = None) -> None:
    with SessionLocal() as db:
        evaluation = db.query(Evaluation).filter(Evaluation.job_id == job_id).first()
        if evaluation:
            previous_status = evaluation.status
            evaluation.status = status.value
            db.add(AuditLog(actor_user_id=None,organization_id=None,action='STATUS_CHANGED',resource_type='evaluation',resource_id=job_id,metadata_json={'previous_status': previous_status,'new_status': status.value,'detail': detail,'source': 'worker'}))
            db.commit()


@celery_app.task(bind=True,name='prepared.send_invitation_email',max_retries=3,default_retry_delay=60)
def send_invitation_email_task(self, invitation_id: int):
    with SessionLocal() as db:
        invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
        if not invitation:
            return {'delivered': False, 'reason': 'invitation_not_found'}

        invitation.delivery_attempts = (invitation.delivery_attempts or 0) + 1
        invitation.delivery_status = 'sending'
        db.commit()

        try:
            delivered = send_invitation_email(invitation.email, invitation.token)
            invitation.delivery_status = 'sent' if delivered else 'disabled'
            invitation.last_delivery_error = None if delivered else 'SMTP disabled or provider not configured'
            db.add(AuditLog(actor_user_id=None,organization_id=invitation.organization_id,action='INVITATION_DELIVERY_SENT' if delivered else 'INVITATION_DELIVERY_SKIPPED',resource_type='invitation',resource_id=str(invitation.id),metadata_json={'email': invitation.email,'attempts': invitation.delivery_attempts}))
            db.commit()
            return {'delivered': delivered, 'email': invitation.email}
        except Exception as exc:
            error = str(exc)
            invitation.delivery_status = 'failed'
            invitation.last_delivery_error = error[:500]
            db.add(AuditLog(actor_user_id=None,organization_id=invitation.organization_id,action='INVITATION_DELIVERY_FAILED',resource_type='invitation',resource_id=str(invitation.id),metadata_json={'email': invitation.email,'attempts': invitation.delivery_attempts,'error': error[:500]}))
            db.commit()
            raise self.retry(exc=exc)


@celery_app.task(name="prepared.evaluate")
def evaluate_job(job_id: str, predictions_path: str):
    try:
        update_status(job_id, JobStatus.VALIDATING, "Prediction file accepted; starting validation.")
        update_db_status(job_id, JobStatus.VALIDATING, "Prediction file accepted; starting validation.")
        update_status(job_id, JobStatus.RUNNING, "PREPARED evaluation engine is running.")
        update_db_status(job_id, JobStatus.RUNNING, "PREPARED evaluation engine is running.")
        report = run_prepared_evaluation(repo_root=settings.repo_root,predictions_csv=Path(predictions_path),report_path=report_path(job_id),points_path=points_path(job_id))
        update_status(job_id, JobStatus.COMPLETED, "Evaluation completed successfully.")
        update_db_status(job_id, JobStatus.COMPLETED, "Evaluation completed successfully.")
        return report
    except Exception as exc:
        detail = str(exc)
        update_status(job_id, JobStatus.FAILED, detail)
        update_db_status(job_id, JobStatus.FAILED, detail)
        raise
