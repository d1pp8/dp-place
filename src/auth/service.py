from fastapi import HTTPException, status

from src.auth.repository import UserRepository
from src.auth.schemas import UserIn, TokenResponse
from src.auth.models import User
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
        valid = Security.verify_password(password=password, hashed_password=user.hashed_password)
        if user is None or not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        access_token = Security.create_access_token(user.id, user.role)
        refresh_token = Security.create_refresh_token(user.id)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)



    @staticmethod
    def _new_user(data: UserIn, hashed_password: str) -> dict:
        return {
            "email": data.email,
            "hashed_password": hashed_password,
            "role": data.role,
        }
