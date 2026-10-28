from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

from src.core.config import settings


password_hash = PasswordHash.recommended()

class Security:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return password_hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return password_hash.verify(password, hashed_password)


    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        return Security._create_token(
            data={"sub": str(user_id), "role": role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            token_type="access"
        )

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        return Security._create_token(
            data={"sub": str(user_id)},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_type="refresh"
        )

    @staticmethod
    def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire, "type": token_type})
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )