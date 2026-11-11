from sqladmin.authentication import AuthenticationBackend
from fastapi import Request

from src.auth.models import UserRole
from src.auth.repository import UserRepository
from src.core.database import async_session_maker
from src.core.security import Security

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username", "")).lower()
        password = str(form.get("password", ""))

        async with async_session_maker() as session:
            user =  await UserRepository(session).get_by_email(email)

        if user is None or not user.is_active or user.role != UserRole.ADMIN:
            return False
        if not await Security.verify_password(password=password, hashed_password=user.hashed_password):
            return False

        request.session.update({"admin_user_uuid": user.uuid})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_uuid = request.session.get("admin_user_uuid")
        if not user_uuid:
            return False

        async with async_session_maker() as session:
            user = await UserRepository(session).get_by_uuid(user_uuid)
        return bool(user and user.is_active and user.role == UserRole.ADMIN)

