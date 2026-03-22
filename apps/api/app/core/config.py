from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "TASKFLOW_"}

    app_name: str = "TaskFlow API"
    debug: bool = False
    version: str = "0.1.0"

    database_url: str = "postgresql+asyncpg://taskflow:taskflow@localhost:5432/taskflow"

    jwt_secret_key: str = "change-me-in-production"  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
