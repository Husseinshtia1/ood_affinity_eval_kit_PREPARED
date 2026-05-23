from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .rbac import require_roles

router = APIRouter(prefix='/organization', tags=['organization'])


@router.get('/users')
def list_organization_users(
    current_user: User = Depends(require_roles('owner', 'admin')),
    db: Session = Depends(get_db),
):
    users = (
        db.query(User)
        .filter(User.organization_id == current_user.organization_id)
        .order_by(User.id.asc())
        .all()
    )

    return {
        'items': [
            {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'organization_id': user.organization_id,
                'created_at': user.created_at.isoformat() if user.created_at else None,
            }
            for user in users
        ]
    }
