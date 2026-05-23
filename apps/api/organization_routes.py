from secrets import token_urlsafe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .audit import write_audit_event
from .auth_security import hash_password
from .database import get_db
from .models import User
from .rbac import require_roles

router = APIRouter(prefix='/organization', tags=['organization'])


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: str = Field(default='member', pattern='^(member|admin)$')


@router.get('/users')
def list_organization_users(current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    users = db.query(User).filter(User.organization_id == current_user.organization_id).order_by(User.id.asc()).all()
    return {'items': [{'id': user.id,'email': user.email,'role': user.role,'organization_id': user.organization_id,'created_at': user.created_at.isoformat() if user.created_at else None} for user in users]}


@router.post('/users/invite')
def invite_user(data: InviteUserRequest,current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already exists')

    temporary_password = token_urlsafe(18)
    user = User(email=data.email,hashed_password=hash_password(temporary_password),role=data.role,organization_id=current_user.organization_id)
    db.add(user)
    db.flush()

    write_audit_event(db,'USER_INVITED','user',str(user.id),actor=current_user,metadata={'email': data.email, 'role': data.role})
    db.commit()

    return {'id': user.id,'email': user.email,'role': user.role,'temporary_password': temporary_password,'message': 'User created with a temporary password. Email delivery is not configured yet.'}
