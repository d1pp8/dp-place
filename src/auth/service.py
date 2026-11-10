from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.repository import UserRepository
from src.auth.schemas import UserIn, TokenResponse
from src.auth.models import User
from src.core.config import settings
from src.core.security import Security
from src.core.exceptions import (
    EmailAlreadyExists,
    InvalidCredentials,
    InactiveUser,
    InvalidToken,
    InvalidTokenType,
    TokenReuseDetected,
    UserNotFoundOrInactive
)


class AuthService:
    def __init__(self, repository: UserRepository, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def register_user(self, user_data: UserIn) -> User:
        email = user_data.email.lower()
        if await self.repository.get_by_email(email):
            raise EmailAlreadyExists

        hashed_password = await Security.get_password_hash(user_data.password)
        user_dict = {"email": email, "hashed_password": hashed_password}
        try:
            user = await self.repository.create(user_dict)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise EmailAlreadyExists from None
        return user



    async def authenticate_user(self, email: str, password: str, redis: Redis) -> TokenResponse | None:
        email = email.lower()
        user = await self.repository.get_by_email(email=email)

        hashed = user.hashed_password if user else Security.TMP_HASH
        verified_password = await Security.verify_password(password=password, hashed_password=hashed)

        if user is None or not verified_password:
            raise InvalidCredentials

        if not user.is_active:
            raise InactiveUser

        access_token = Security.create_access_token(user.id, user.role)
        refresh_token, jti = Security.create_refresh_token(user.id)

        refresh_expire_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        await redis.set(name=f"refresh_token:{user.id}:{jti}", value="active", ex=refresh_expire_seconds)

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)


    async def refresh_tokens(self, refresh_token: str, redis: Redis) -> TokenResponse:
        payload = Security.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidTokenType

        try:
            user_id = int(payload.get("sub"))
            jti = payload.get("jti")
            if not jti:
                raise ValueError("Missing jti")
        except (ValueError, TypeError) as e:
            raise InvalidToken from e

        redis_key = f"refresh_token:{user_id}:{jti}"
        is_active = await redis.getdel(redis_key)

        if not is_active:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=f"refresh_token:{user_id}:*", count=100)
                if keys:
                    await redis.delete(*keys)
                if cursor == 0:
                    break
            raise TokenReuseDetected

        user = await self.repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise UserNotFoundOrInactive

        access_token = Security.create_access_token(user_id, user.role)
        new_refresh_token, new_jti = Security.create_refresh_token(user_id)
        refresh_expire_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        await redis.set(name=f"refresh_token:{user.id}:{new_jti}", value="active", ex=refresh_expire_seconds)

        return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


    async def logout(self, token: str, refresh_token: str | None, redis: Redis) -> dict:
        expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        await redis.set(name=f"blacklist:{token}", value="revoked", ex=expire_seconds)

        if  refresh_token:
            try:
                payload = Security.decode_token(refresh_token)
                if payload.get("type") == "refresh":
                    user_id = payload.get("sub")
                    jti = payload.get("jti")
                    await redis.delete(f"refresh_token:{user_id}:{jti}")
            except Exception:
                pass
        return {"detail": "Successfully logged out"}

