from fastapi import APIRouter, Depends

from .auth_dependencies import get_current_user
from .auth_schemas import UserResponse
from .models import User

router = APIRouter(prefix='/auth', tags=['auth'])


@router.get('/me', response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
