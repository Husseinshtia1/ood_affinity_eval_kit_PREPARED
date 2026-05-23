from pathlib import Path
from datetime import datetime, timezone

from worker.celery_app import celery_app
from apps.api.prepared_runner import run_prepared_evaluation
from apps.api.settings import get_settings
from apps.api.schemas import JobStatus
from apps.api.storage import report_path, points_path, update_status
from apps.api.database import SessionLocal
from apps.api.models import Evaluation, AuditLog, Invitation
from apps.api.notifications import send_invitation_email

settings = get_settings()

# existing methods omitted for brevity ...

@celery_app.task(name='prepared.cleanup_expired_invitations')
def cleanup_expired_invitations():
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)
        invitations = db.query(Invitation).filter(
            Invitation.accepted_at.is_(None),
            Invitation.expires_at < now
        ).all()

        deleted=0
        for invitation in invitations:
            db.add(AuditLog(
                actor_user_id=None,
                organization_id=invitation.organization_id,
                action='INVITATION_EXPIRED_CLEANED',
                resource_type='invitation',
                resource_id=str(invitation.id),
                metadata_json={'email': invitation.email}
            ))
            db.delete(invitation)
            deleted += 1

        db.commit()
        return {'deleted': deleted}
