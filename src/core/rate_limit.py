from fastapi import HTTPException, Request, status
from src.core.redis import RedisDep
from fastapi import Depends


def rate_limit(name: str, limit: int, window_seconds: int):
    async def dependency(request: Request, redis: RedisDep):
        ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{name}:{ip}"

        async with redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            await pipe.expire(key, window_seconds, nx=True)
            await pipe.ttl(key)
            count, _, ttl, = await pipe.execute()

        if count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Try again later",
                headers={"Retry-After": str(max(ttl,1))}
            )
    return dependency


register_rate_limit = Depends(rate_limit("register", limit=10, window_seconds=3600))
login_rate_limit = Depends(rate_limit("login", limit=10, window_seconds=120))