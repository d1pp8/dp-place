from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any, Annotated

from src.auth.schemas import UserIn, UserOut, TokenResponse
from src.auth.dependencies import AuthServiceDep, CurrentUserDep


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(service: AuthServiceDep, user: UserIn) -> Any:
    return await service.register_user(user_data=user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthServiceDep
) -> Any:
    return await service.authenticate_user(
        email=form_data.username, password=form_data.password
    )

@router.get("/me", response_model=UserOut)
async def get_me(current_user: CurrentUserDep):
    return current_user