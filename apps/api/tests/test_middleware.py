import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
)


def _make_app(*middlewares) -> FastAPI:
    """Create a minimal app with given middlewares for testing."""
    test_app = FastAPI()

    @test_app.get("/test")
    async def test_route():
        return {"ok": True}

    @test_app.get("/api/v1/auth/login")
    async def login_route():
        return {"ok": True}

    @test_app.get("/api/v1/auth/register")
    async def register_route():
        return {"ok": True}

    for mw in reversed(middlewares):
        if isinstance(mw, tuple):
            test_app.add_middleware(mw[0], **mw[1])
        else:
            test_app.add_middleware(mw)
    return test_app


async def _client(app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestRequestIDMiddleware:
    @pytest.mark.asyncio
    async def test_adds_request_id_header(self):
        app = _make_app(RequestIDMiddleware)
        async with await _client(app) as client:
            response = await client.get("/test")
            assert "x-request-id" in response.headers

    @pytest.mark.asyncio
    async def test_uses_provided_request_id(self):
        app = _make_app(RequestIDMiddleware)
        async with await _client(app) as client:
            response = await client.get(
                "/test", headers={"X-Request-ID": "my-custom-id"}
            )
            assert response.headers["x-request-id"] == "my-custom-id"


class TestSecurityHeadersMiddleware:
    @pytest.mark.asyncio
    async def test_adds_security_headers(self):
        app = _make_app(SecurityHeadersMiddleware)
        async with await _client(app) as client:
            response = await client.get("/test")
            assert response.headers["x-content-type-options"] == "nosniff"
            assert response.headers["x-frame-options"] == "DENY"
            assert response.headers["x-xss-protection"] == "1; mode=block"
            assert (
                response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
            )


class TestStructuredLoggingMiddleware:
    @pytest.mark.asyncio
    async def test_request_completes_with_logging(self):
        app = _make_app(RequestIDMiddleware, StructuredLoggingMiddleware)
        async with await _client(app) as client:
            response = await client.get("/test")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_logging_without_request_id(self):
        app = _make_app(StructuredLoggingMiddleware)
        async with await _client(app) as client:
            response = await client.get("/test")
            assert response.status_code == 200


class TestRateLimitMiddleware:
    @pytest.mark.asyncio
    async def test_non_auth_path_not_limited(self):
        app = _make_app((RateLimitMiddleware, {"max_requests": 2}))
        async with await _client(app) as client:
            for _ in range(10):
                response = await client.get("/test")
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_path_rate_limited(self):
        app = _make_app((RateLimitMiddleware, {"max_requests": 2}))
        async with await _client(app) as client:
            # First 2 should pass
            for _ in range(2):
                response = await client.get("/api/v1/auth/login")
                assert response.status_code == 200

            # Third should be rate limited
            response = await client.get("/api/v1/auth/login")
            assert response.status_code == 429
            assert response.json()["code"] == "RATE_LIMIT_EXCEEDED"

    @pytest.mark.asyncio
    async def test_rate_limit_register_endpoint(self):
        app = _make_app((RateLimitMiddleware, {"max_requests": 1}))
        async with await _client(app) as client:
            await client.get("/api/v1/auth/register")
            response = await client.get("/api/v1/auth/register")
            assert response.status_code == 429
