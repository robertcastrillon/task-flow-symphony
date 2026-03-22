from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


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

    @application.get("/api/v1/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.version}

    return application


app = create_app()
