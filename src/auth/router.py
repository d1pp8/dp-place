from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any, Annotated

from src.core.redis import RedisDep
from src.auth.schemas import UserIn, UserOut, TokenResponse, RefreshTokenRequest
from src.auth.dependencies import AuthServiceDep, CurrentUserDep, TokenDep

from src.core.rate_limit import register_rate_limit, login_rate_limit


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

OAuthFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, dependencies=[register_rate_limit])
async def register(service: AuthServiceDep, user: UserIn) -> Any:
    return await service.register_user(user_data=user)


@router.post("/login", response_model=TokenResponse, dependencies=[login_rate_limit])
async def login(form_data: OAuthFormDep, service: AuthServiceDep, redis: RedisDep) -> Any:
    return await service.authenticate_user(email=form_data.username, password=form_data.password, redis=redis)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_toke(body: RefreshTokenRequest, service: AuthServiceDep, redis: RedisDep):
    return await service.refresh_tokens(refresh_token=body.refresh_token, redis=redis)


@router.post("/logout")
async def logout(token: TokenDep, current_user: CurrentUserDep, redis: RedisDep, service: AuthServiceDep, rt: RefreshTokenRequest | None = None):
    return await service.logout(token=token, redis=redis, refresh_token=rt.refresh_token if rt else None)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: CurrentUserDep):
    return current_user