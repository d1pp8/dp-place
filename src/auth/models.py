from datetime import datetime
from enum import StrEnum

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import BaseModel

class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"
    SELLER = "seller"

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    is_active: Mapped[bool] = mapped_column(default=True)
