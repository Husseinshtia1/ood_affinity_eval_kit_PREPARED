from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .audit import write_audit_event
from .auth_security import hash_password
from .database import get_db
from .models import Invitation, User

router=APIRouter(prefix='/auth',tags=['auth'])

class AcceptInvitationRequest(BaseModel):
    token:str
    password:str=Field(min_length=8,max_length=128)

@router.post('/accept-invitation')
def accept_invitation(data:AcceptInvitationRequest,db:Session=Depends(get_db)):
    invitation=db.query(Invitation).filter(Invitation.token==data.token).first()

    if not invitation:
      raise HTTPException(status_code=404,detail='Invitation not found')

    if invitation.accepted_at:
      raise HTTPException(status_code=400,detail='Invitation already used')

    if invitation.expires_at < datetime.now(timezone.utc):
      raise HTTPException(status_code=400,detail='Invitation expired')

    user=User(email=invitation.email,hashed_password=hash_password(data.password),role=invitation.role,organization_id=invitation.organization_id)
    db.add(user)
    db.flush()

    invitation.accepted_at=datetime.now(timezone.utc)

    write_audit_event(db,'INVITATION_ACCEPTED','user',str(user.id),actor=user)
    db.commit()

    return {'id':user.id,'email':user.email,'role':user.role}
