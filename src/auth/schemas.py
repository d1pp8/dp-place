from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.auth.models import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.BUYER


class UserIn(UserBase):
    password: str = Field(min_length=8)


class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
