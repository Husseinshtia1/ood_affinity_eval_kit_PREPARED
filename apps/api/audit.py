from sqlalchemy.orm import Session

from .models import AuditLog, User


def write_audit_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    actor: User | None = None,
    organization_id: int | None = None,
    metadata: dict | None = None,
) -> None:
    event = AuditLog(
        actor_user_id=actor.id if actor else None,
        organization_id=organization_id or (actor.organization_id if actor else None),
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=metadata,
    )
    db.add(event)
