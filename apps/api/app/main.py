from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.middleware import (
    RateLimitMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
)
from app.routers.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
    )

    # CORS must be outermost
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware chain (outermost → innermost):
    # rate limiting → security headers → request ID → structured logging
    application.add_middleware(RateLimitMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(StructuredLoggingMiddleware)

    # Global error handler — standard JSON format
    @application.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
        )

    from app.routers import auth, comments, dashboard, tasks, users

    application.include_router(health_router, prefix="/api/v1")
    application.include_router(auth.router)
    application.include_router(users.router)
    application.include_router(tasks.router)
    application.include_router(comments.router)
    application.include_router(dashboard.router)

    return application


app = create_app()
