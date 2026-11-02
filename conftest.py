from typing import AsyncGenerator
import sys
import asyncio

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from redis.asyncio import Redis

from src.main import app
from src.core.database import Base, get_async_session
from src.core.redis import get_redis
from src.core.config import settings

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

assert settings.POSTGRESQL_TEST_NAME.startswith("test_")
assert settings.POSTGRESQL_TEST_NAME != settings.POSTGRESQL_NAME
assert settings.REDIS_TEST_DB != 0


test_engine = create_async_engine(settings.TEST_DATABASE)
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_maker() as session:
        yield session

async def override_get_redis():
    redis = Redis.from_url(settings.TEST_REDIS, decode_responses=True)
    yield redis
    await redis.aclose()


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_redis] = override_get_redis


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

    redis = Redis.from_url(settings.TEST_REDIS)
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def registered_user(async_client: AsyncClient) -> dict:
    payload = {
        "email": "test-test@test.com",
        "password": "123123123"
    }
    await async_client.post("/api/v1/auth/register", json=payload)
    return payload

@pytest_asyncio.fixture
async def auth_tokens(async_client: AsyncClient, registered_user) -> dict:
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": registered_user["email"], "password": registered_user["password"]}
    )
    return response.json()

@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient, auth_tokens) -> AsyncClient:
    async_client.headers = {"Authorization": f"Bearer {auth_tokens["access_token"]}"}
    return async_client
