from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .auth_dependencies import get_current_user
from .database import get_db
from .models import AuditLog, User

router = APIRouter(prefix='/audit', tags=['audit'])


@router.get('')
def list_audit_events(
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    events = (
        db.query(AuditLog)
        .filter(AuditLog.organization_id == current_user.organization_id)
        .order_by(AuditLog.id.desc())
        .limit(limit)
        .all()
    )

    return {
        'items': [
            {
                'id': event.id,
                'actor_user_id': event.actor_user_id,
                'organization_id': event.organization_id,
                'action': event.action,
                'resource_type': event.resource_type,
                'resource_id': event.resource_id,
                'metadata': event.metadata_json,
                'created_at': event.created_at.isoformat() if event.created_at else None,
            }
            for event in events
        ]
    }
