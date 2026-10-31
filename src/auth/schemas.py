from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.auth.models import UserRole


class UserBase(BaseModel):
    email: EmailStr


class UserIn(UserBase):
    password: str = Field(min_length=8)


class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
