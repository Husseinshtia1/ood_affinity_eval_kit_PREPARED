from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from .audit import write_audit_event
from .database import get_db
from .models import User, Invitation
from .rbac import require_roles

router = APIRouter(prefix='/organization', tags=['organization'])


class InviteUserRequest(BaseModel):
    email: EmailStr
    role: str = Field(default='member', pattern='^(member|admin)$')


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(pattern='^(member|admin|owner)$')


@router.get('/users')
def list_organization_users(current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    users = db.query(User).filter(User.organization_id == current_user.organization_id).order_by(User.id.asc()).all()
    return {'items': [{'id': user.id,'email': user.email,'role': user.role,'organization_id': user.organization_id,'created_at': user.created_at.isoformat() if user.created_at else None} for user in users]}


@router.post('/users/invite')
def invite_user(data: InviteUserRequest,current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already exists')

    token = token_urlsafe(32)
    invitation = Invitation(
        email=data.email,
        role=data.role,
        token=token,
        organization_id=current_user.organization_id,
        invited_by_user_id=current_user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=72),
    )
    db.add(invitation)
    db.flush()

    write_audit_event(db,'USER_INVITED','invitation',str(invitation.id),actor=current_user,metadata={'email': data.email, 'role': data.role})
    db.commit()

    return {'invitation_id': invitation.id,'email': invitation.email,'role': invitation.role,'invitation_token': token,'expires_at': invitation.expires_at.isoformat(),'message': 'Invitation created. Email delivery is not configured yet.'}


@router.patch('/users/{user_id}/role')
def update_user_role(user_id:int,data:UpdateUserRoleRequest,current_user:User=Depends(require_roles('owner')),db:Session=Depends(get_db)):
    target=db.query(User).filter(User.id==user_id,User.organization_id==current_user.organization_id).first()
    if not target:
        raise HTTPException(status_code=404,detail='User not found')

    previous_role=target.role
    if previous_role=='owner' and data.role!='owner':
        owner_count=db.query(User).filter(User.organization_id==current_user.organization_id,User.role=='owner').count()
        if owner_count<=1:
            raise HTTPException(status_code=400,detail='Cannot demote the last owner')

    target.role=data.role
    write_audit_event(db,'USER_ROLE_CHANGED','user',str(target.id),actor=current_user,metadata={'previous_role':previous_role,'new_role':data.role})
    db.commit()

    return {'id':target.id,'email':target.email,'role':target.role}
