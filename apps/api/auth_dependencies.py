from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .auth_security import decode_access_token
from .database import get_db
from .models import User

security=HTTPBearer()


def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(security),db:Session=Depends(get_db)):
    email=decode_access_token(credentials.credentials)
    user=db.query(User).filter(User.email==email).first()

    if not user:
        raise HTTPException(status_code=401,detail='User not found')

    return user
