from collections.abc import Callable
from fastapi import Depends, HTTPException

from .auth_dependencies import get_current_user
from .models import User


def require_roles(*allowed_roles: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail='Insufficient role permissions')
        return current_user

    return dependency
