from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from src.core.config import settings

redis_client = Redis.from_url(url=settings.REDIS_URL, decode_responses=True)


async def get_redis() -> AsyncGenerator[Redis]:
    yield redis_client


RedisDep = Annotated[Redis, Depends(get_redis)]
