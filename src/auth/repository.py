import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: dict) -> User:
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_uuid(self, user_uuid: uuid.UUID) -> User | None:
        query = select(User).where(User.uuid == user_uuid)
        user = await self.session.execute(query)
        return user.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        user = await self.session.execute(query)
        return user.scalar_one_or_none()
