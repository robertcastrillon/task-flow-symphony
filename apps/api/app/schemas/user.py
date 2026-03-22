import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

<<<<<<< HEAD
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
=======

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    avatar_url: str | None = None
    role: str
    telegram_chat_id: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
>>>>>>> origin/eng-88


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
<<<<<<< HEAD
    avatar_url: str | None = None


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    name: str
    avatar_url: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
=======
    avatar_url: str | None = Field(None, max_length=500)
>>>>>>> origin/eng-88
