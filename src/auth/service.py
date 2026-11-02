from fastapi import HTTPException, status
from redis.asyncio import Redis

from src.auth.repository import UserRepository
from src.auth.schemas import UserIn, TokenResponse
from src.auth.models import User
from src.core.config import settings
from src.core.security import Security


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register_user(self, user_data: UserIn) -> User:
        if await self.repository.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed_password = Security.get_password_hash(user_data.password)
        new_user = self._new_user(data=user_data, hashed_password=hashed_password)
        return await self.repository.create(new_user)

    async def authenticate_user(self, email: str, password: str) -> TokenResponse | None:
        user = await self.repository.get_by_email(email=email)
        if user is None or not Security.verify_password(
                password=password,
                hashed_password=user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = Security.create_access_token(user.id, user.role)
        refresh_token = Security.create_refresh_token(user.id)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = Security.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = int(payload.get("sub"))
        user = await self.repository.get_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not fount or inactive"
            )
        access_token = Security.create_access_token(user_id, user.role)
        refresh_token = Security.create_refresh_token(user_id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def logout(self, token: str, redis: Redis) -> dict:
        expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        await redis.setex(f"blacklist:{token}", expire_seconds, "revoked")
        return {"detail": "Successfully logged out"}

    @staticmethod
    def _new_user(data: UserIn, hashed_password: str) -> dict:
        return {
            "email": data.email,
            "hashed_password": hashed_password,
        }
