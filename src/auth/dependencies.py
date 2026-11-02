from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.security import Security
from src.core.database import SessionDep
from src.core.redis import RedisDep
from src.auth.models import User, UserRole
from src.auth.repository import UserRepository
from src.auth.service import AuthService


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)

RepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

def get_auth_service(repository: RepositoryDep) -> AuthService:
    return AuthService(repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(token: TokenDep, repository: RepositoryDep, redis: RedisDep) -> User:
    is_blacklisted = await redis.get(f"blacklist:{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked (logged out)."
        )

    payload = Security.decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token."
        )
    user_id = int(payload.get("sub"))
    user = await repository.get_by_id(user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive."
        )
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: CurrentUserDep) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions."
            )
        return user

AdminDep = Annotated[User, Depends(RoleChecker([UserRole.ADMIN]))]
