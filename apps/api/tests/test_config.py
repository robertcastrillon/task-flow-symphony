from app.core.config import Settings


def test_default_settings():
    s = Settings()
    assert s.app_name == "TaskFlow API"
    assert s.debug is False
    assert s.version == "0.1.0"
    assert s.jwt_algorithm == "HS256"
    assert s.jwt_access_token_expire_minutes == 1440


def test_jwt_refresh_token_defaults():
    s = Settings()
    assert s.jwt_refresh_token_expire_minutes == 10080


def test_rate_limit_defaults():
    s = Settings()
    assert s.rate_limit_auth == 5


def test_cors_origins_default():
    s = Settings()
    assert "http://localhost:5173" in s.cors_origins


def test_database_url_default():
    s = Settings()
    assert "postgresql" in s.database_url
    assert "taskflow" in s.database_url
