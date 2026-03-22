from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "TASKFLOW_"}

    app_name: str = "TaskFlow API"
    debug: bool = False
<<<<<<< HEAD

    database_url: str = "postgresql+asyncpg://taskflow:taskflow@localhost:5432/taskflow"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24h
    jwt_refresh_token_expire_minutes: int = 10080  # 7 days

    cors_origins: list[str] = ["http://localhost:5173"]

    rate_limit_auth: int = 5  # requests per minute

=======
    version: str = "0.1.0"

    database_url: str = "postgresql+asyncpg://taskflow:taskflow@localhost:5432/taskflow"

    jwt_secret_key: str = "change-me-in-production"  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440  # 24 hours

    cors_origins: list[str] = ["http://localhost:5173"]

>>>>>>> origin/eng-88

settings = Settings()
