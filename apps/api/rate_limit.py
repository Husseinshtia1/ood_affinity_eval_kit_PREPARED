from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

import redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .settings import get_settings


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.redis_client = None
        if self.settings.rate_limit_backend == 'redis':
            self.redis_client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True)

    def client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',', 1)[0].strip()
        if request.client:
            return request.client.host
        return 'unknown'

    def rate_limit_response(self, retry_after: int) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={'detail': 'Rate limit exceeded'},
            headers={'Retry-After': str(retry_after)},
        )

    def check_memory_limit(self, key: str) -> tuple[bool, int, int]:
        now = time.time()
        window = self.settings.rate_limit_window_seconds
        max_requests = self.settings.rate_limit_requests
        events = self.requests[key]

        while events and events[0] <= now - window:
            events.popleft()

        if len(events) >= max_requests:
            retry_after = max(1, int(window - (now - events[0])))
            return False, retry_after, 0

        events.append(now)
        remaining = max(0, max_requests - len(events))
        return True, window, remaining

    def check_redis_limit(self, key: str) -> tuple[bool, int, int]:
        if self.redis_client is None:
            return self.check_memory_limit(key)

        window = self.settings.rate_limit_window_seconds
        max_requests = self.settings.rate_limit_requests
        bucket = int(time.time() // window)
        redis_key = f'prepared:rate_limit:{key}:{bucket}'

        count = int(self.redis_client.incr(redis_key))
        if count == 1:
            self.redis_client.expire(redis_key, window)

        remaining = max(0, max_requests - count)
        if count > max_requests:
            ttl = self.redis_client.ttl(redis_key)
            retry_after = ttl if ttl and ttl > 0 else window
            return False, retry_after, remaining

        return True, window, remaining

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not self.settings.rate_limit_enabled:
            return await call_next(request)

        key = self.client_key(request)
        if self.settings.rate_limit_backend == 'redis':
            allowed, retry_after, remaining = self.check_redis_limit(key)
        else:
            allowed, retry_after, remaining = self.check_memory_limit(key)

        if not allowed:
            return self.rate_limit_response(retry_after)

        response = await call_next(request)
        response.headers['X-RateLimit-Limit'] = str(self.settings.rate_limit_requests)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        response.headers['X-RateLimit-Window'] = str(self.settings.rate_limit_window_seconds)
        response.headers['X-RateLimit-Backend'] = self.settings.rate_limit_backend
        return response
