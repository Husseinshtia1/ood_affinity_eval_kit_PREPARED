from apps.api.auth_security import create_access_token
from apps.api.rate_limit import InMemoryRateLimitMiddleware


class DummyApp:
    async def __call__(self, scope, receive, send):
        pass


class DummyClient:
    host = '127.0.0.1'


class DummyRequest:
    def __init__(self, headers):
        self.headers = headers
        self.client = DummyClient()


def test_rate_limit_uses_org_aware_jwt_key():
    middleware = InMemoryRateLimitMiddleware(DummyApp())
    token = create_access_token(
        'user@example.com',
        extra_claims={
            'organization_id': 42,
            'role': 'owner'
        }
    )
    request = DummyRequest({'authorization': f'Bearer {token}'})

    assert middleware.client_key(request) == 'org:42:user:user@example.com'


def test_rate_limit_falls_back_to_ip_without_token():
    middleware = InMemoryRateLimitMiddleware(DummyApp())
    request = DummyRequest({})

    assert middleware.client_key(request) == 'ip:127.0.0.1'
