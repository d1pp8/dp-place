from datetime import datetime
from enum import StrEnum

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserRole(StrEnum):
    ADMIN = "admin"
    BUYER = "buyer"
    SELLER = "seller"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    role: Mapped[UserRole] = mapped_column(default=UserRole.BUYER)

    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
