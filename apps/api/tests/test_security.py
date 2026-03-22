from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    JWTError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_returns_bcrypt_hash(self):
        hashed = hash_password("mypassword")
        assert hashed.startswith("$2b$")

    def test_hash_password_different_each_time(self):
        h1 = hash_password("mypassword")
        h2 = hash_password("mypassword")
        assert h1 != h2

    def test_verify_password_correct(self):
        hashed = hash_password("secret123")
        assert verify_password("secret123", hashed) is True

    def test_verify_password_wrong(self):
        hashed = hash_password("secret123")
        assert verify_password("wrongpass", hashed) is False


class TestAccessToken:
    def test_create_access_token_decodable(self):
        token = create_access_token({"sub": "user-123"})
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == "user-123"
        assert payload["type"] == "access"

    def test_create_access_token_has_expiry(self):
        token = create_access_token({"sub": "user-123"})
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert "exp" in payload


class TestRefreshToken:
    def test_create_refresh_token_decodable(self):
        token = create_refresh_token({"sub": "user-456"})
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == "user-456"
        assert payload["type"] == "refresh"

    def test_create_refresh_token_has_expiry(self):
        token = create_refresh_token({"sub": "user-456"})
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert "exp" in payload


class TestDecodeToken:
    def test_decode_valid_token(self):
        token = create_access_token({"sub": "user-789"})
        payload = decode_token(token)
        assert payload["sub"] == "user-789"
        assert payload["type"] == "access"

    def test_decode_invalid_token_raises(self):
        with pytest.raises(JWTError):
            decode_token("not-a-real-token")

    def test_decode_expired_token_raises(self):
        expired_payload = {
            "sub": "user-123",
            "exp": datetime.now(tz=UTC) - timedelta(hours=1),
            "type": "access",
        }
        token = jwt.encode(
            expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )
        with pytest.raises(JWTError):
            decode_token(token)

    def test_decode_wrong_secret_raises(self):
        token = jwt.encode(
            {"sub": "user-123", "type": "access"},
            "wrong-secret",
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(JWTError):
            decode_token(token)
