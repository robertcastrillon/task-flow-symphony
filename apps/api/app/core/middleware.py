import time
import uuid
from collections import defaultdict

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse

from app.core.config import settings

logger = structlog.get_logger()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add a unique request ID to each request for correlation."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add standard security headers to all responses."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with structured logging."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        request_id = getattr(request.state, "request_id", "unknown")
        await logger.ainfo(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting for auth endpoints."""

    AUTH_PATHS = {"/api/v1/auth/register", "/api/v1/auth/login"}
    _instances: list["RateLimitMiddleware"] = []

    def __init__(self, app, max_requests: int | None = None):
        super().__init__(app)
        self.max_requests = max_requests or settings.rate_limit_auth
        self.window_seconds = 60
        self._requests: dict[str, list[float]] = defaultdict(list)
        RateLimitMiddleware._instances.append(self)

    @classmethod
    def reset_all(cls) -> None:
        """Clear rate limit state on all instances (useful for tests)."""
        for instance in cls._instances:
            instance._requests.clear()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path not in self.AUTH_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()

        # Clean old entries
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if now - t < self.window_seconds
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests",
                    "code": "RATE_LIMIT_EXCEEDED",
                },
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
