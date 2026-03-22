import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.deps import get_current_user, require_admin
from app.core.security import create_access_token, create_refresh_token


def _make_user(role="member", is_active=True, user_id=None):
    return SimpleNamespace(
        id=user_id or uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        role=role,
        is_active=is_active,
    )


def _mock_db_returning(user):
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    db.execute.return_value = result
    return db


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_no_credentials_raises_401(self):
        db = AsyncMock()
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None, db=db)
        assert exc_info.value.status_code == 401
        assert "Not authenticated" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        db = AsyncMock()
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad-token")
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds, db=db)
        assert exc_info.value.status_code == 401
        assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_token_type_raises_401(self):
        db = AsyncMock()
        token = create_refresh_token({"sub": str(uuid.uuid4())})
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds, db=db)
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_token_without_sub_raises_401(self):
        db = AsyncMock()
        token = create_access_token({})  # no "sub"
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds, db=db)
        assert exc_info.value.status_code == 401
        assert "Invalid token payload" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_user_not_found_raises_401(self):
        db = _mock_db_returning(None)
        user_id = uuid.uuid4()
        token = create_access_token({"sub": str(user_id)})
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds, db=db)
        assert exc_info.value.status_code == 401
        assert "User not found or inactive" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_inactive_user_raises_401(self):
        user = _make_user(is_active=False)
        db = _mock_db_returning(user)
        token = create_access_token({"sub": str(user.id)})
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=creds, db=db)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self):
        user = _make_user()
        db = _mock_db_returning(user)
        token = create_access_token({"sub": str(user.id)})
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        result = await get_current_user(credentials=creds, db=db)
        assert result is user


class TestRequireAdmin:
    @pytest.mark.asyncio
    async def test_admin_user_passes(self):
        user = _make_user(role="admin")
        result = await require_admin(current_user=user)
        assert result is user

    @pytest.mark.asyncio
    async def test_member_user_raises_403(self):
        user = _make_user(role="member")
        with pytest.raises(HTTPException) as exc_info:
            await require_admin(current_user=user)
        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail
