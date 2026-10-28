from typing import Annotated
from fastapi import Depends

from src.core.database import SessionDep
from src.auth.repository import UserRepository
from src.auth.service import AuthService

def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)

def get_auth_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repository)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]