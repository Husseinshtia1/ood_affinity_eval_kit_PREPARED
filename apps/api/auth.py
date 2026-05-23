from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .auth_schemas import RegisterRequest, LoginRequest, TokenResponse
from .auth_security import hash_password, verify_password, create_access_token
from .database import get_db
from .models import Organization, User

router=APIRouter(prefix='/auth',tags=['auth'])

@router.post('/register',response_model=TokenResponse)
def register(data:RegisterRequest,db:Session=Depends(get_db)):
    existing=db.query(User).filter(User.email==data.email).first()
    if existing:
        raise HTTPException(status_code=400,detail='Email already exists')

    org=Organization(name=data.organization_name)
    db.add(org)
    db.flush()

    user=User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role='owner',
        organization_id=org.id
    )

    db.add(user)
    db.commit()

    token=create_access_token(
        data.email,
        extra_claims={
            'organization_id': org.id,
            'role': user.role
        }
    )
    return TokenResponse(access_token=token)

@router.post('/login',response_model=TokenResponse)
def login(data:LoginRequest,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==data.email).first()

    if not user or not verify_password(data.password,user.hashed_password):
        raise HTTPException(status_code=401,detail='Invalid credentials')

    token=create_access_token(
        user.email,
        extra_claims={
            'organization_id': user.organization_id,
            'role': user.role
        }
    )

    return TokenResponse(access_token=token)
