import pytest
from fastapi import HTTPException

from apps.api.rbac import require_roles


class DummyUser:
    def __init__(self, role: str):
        self.role = role


def test_require_roles_allows_allowed_role():
    dependency = require_roles('owner', 'admin')
    user = DummyUser('admin')

    assert dependency(user) is user


def test_require_roles_rejects_disallowed_role():
    dependency = require_roles('owner', 'admin')
    user = DummyUser('member')

    with pytest.raises(HTTPException) as exc:
        dependency(user)

    assert exc.value.status_code == 403
    assert exc.value.detail == 'Insufficient role permissions'
