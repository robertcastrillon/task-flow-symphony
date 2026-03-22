from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
