from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .settings import get_settings


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def client_key(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not self.settings.rate_limit_enabled:
            return await call_next(request)

        now = time.time()
        window = self.settings.rate_limit_window_seconds
        max_requests = self.settings.rate_limit_requests
        key = self.client_key(request)
        events = self.requests[key]

        while events and events[0] <= now - window:
            events.popleft()

        if len(events) >= max_requests:
            retry_after = max(1, int(window - (now - events[0])))
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(retry_after)},
            )

        events.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - len(events)))
        response.headers["X-RateLimit-Window"] = str(window)
        return response
