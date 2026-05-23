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


def serialize_invitation(invitation: Invitation) -> dict:
    now = datetime.now(timezone.utc)
    if invitation.accepted_at:
        status = 'accepted'
    elif invitation.expires_at <= now:
        status = 'expired'
    else:
        status = 'active'
    return {
        'id': invitation.id,
        'email': invitation.email,
        'role': invitation.role,
        'organization_id': invitation.organization_id,
        'invited_by_user_id': invitation.invited_by_user_id,
        'status': status,
        'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None,
        'accepted_at': invitation.accepted_at.isoformat() if invitation.accepted_at else None,
        'created_at': invitation.created_at.isoformat() if invitation.created_at else None,
    }


@router.get('/users')
def list_organization_users(current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    users = db.query(User).filter(User.organization_id == current_user.organization_id).order_by(User.id.asc()).all()
    return {'items': [{'id': user.id,'email': user.email,'role': user.role,'organization_id': user.organization_id,'created_at': user.created_at.isoformat() if user.created_at else None} for user in users]}


@router.get('/invitations')
def list_invitations(current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    invitations = db.query(Invitation).filter(Invitation.organization_id == current_user.organization_id).order_by(Invitation.id.desc()).all()
    return {'items': [serialize_invitation(invitation) for invitation in invitations]}


@router.post('/users/invite')
def invite_user(data: InviteUserRequest,current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already exists')

    now = datetime.now(timezone.utc)
    active_invitation = db.query(Invitation).filter(Invitation.email == data.email,Invitation.organization_id == current_user.organization_id,Invitation.accepted_at.is_(None),Invitation.expires_at > now).first()
    if active_invitation:
        raise HTTPException(status_code=400, detail='Active invitation already exists for this email')

    token = token_urlsafe(32)
    invitation = Invitation(email=data.email,role=data.role,token=token,organization_id=current_user.organization_id,invited_by_user_id=current_user.id,expires_at=now + timedelta(hours=72))
    db.add(invitation)
    db.flush()

    write_audit_event(db,'USER_INVITED','invitation',str(invitation.id),actor=current_user,metadata={'email': data.email, 'role': data.role})
    db.commit()

    return {'invitation_id': invitation.id,'email': invitation.email,'role': invitation.role,'invitation_token': token,'expires_at': invitation.expires_at.isoformat(),'message': 'Invitation created. Email delivery is not configured yet.'}


@router.delete('/invitations/{invitation_id}')
def revoke_invitation(invitation_id:int,current_user: User = Depends(require_roles('owner', 'admin')),db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id,Invitation.organization_id == current_user.organization_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail='Invitation not found')
    if invitation.accepted_at:
        raise HTTPException(status_code=400, detail='Accepted invitations cannot be revoked')

    write_audit_event(db,'INVITATION_REVOKED','invitation',str(invitation.id),actor=current_user,metadata={'email': invitation.email, 'role': invitation.role})
    db.delete(invitation)
    db.commit()
    return {'revoked': True}


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
