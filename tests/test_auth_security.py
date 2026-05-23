from apps.api.auth_security import create_access_token
from jose import jwt
from apps.api.settings import get_settings


def test_token_contains_claims():
    settings = get_settings()
    token = create_access_token(
        'user@example.com',
        extra_claims={
            'organization_id': 123,
            'role': 'owner'
        }
    )

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )

    assert payload['sub'] == 'user@example.com'
    assert payload['organization_id'] == 123
    assert payload['role'] == 'owner'
