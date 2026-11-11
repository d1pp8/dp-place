import jwt
import uuid
import asyncio
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from passlib.context import CryptContext

from src.core.config import settings
from src.core.exceptions import TokenExpired, InvalidToken

password_hash = PasswordHash.recommended()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class Security:
    TMP_HASH = pwd_context.hash("tmp-password-for-timing-attack-protection")

    @staticmethod
    async def get_password_hash(password: str) -> str:
        return await asyncio.to_thread(password_hash.hash, password)

    @staticmethod
    async def verify_password(password: str, hashed_password: str) -> bool:
        return await asyncio.to_thread(password_hash.verify, password, hashed_password)

    @staticmethod
    def create_access_token(user_uuid: uuid.UUID, role: str) -> str:
        return Security._create_token(
            data={"sub": str(user_uuid), "role": role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            token_type="access",
        )

    @staticmethod
    def create_refresh_token(user_uuid: uuid.UUID) -> tuple[str, str]:
        jti = str(uuid.uuid4())
        token =  Security._create_token(
            data={"sub": str(user_uuid), "jti": jti},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_type="refresh",
        )
        return token, jti

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpired
        except jwt.InvalidTokenError:
            raise InvalidToken

    @staticmethod
    def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire, "type": token_type})
        return jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
