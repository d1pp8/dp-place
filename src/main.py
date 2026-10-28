from fastapi import FastAPI
from sqlalchemy import text

from src.core.database import SessionDep
from src.core.redis import RedisDep

from src.auth.router import router as user_router

app = FastAPI(title="dp-place")

app.include_router(user_router)



@app.get("/health")
async def get_database_health(session: SessionDep, redis: RedisDep):
    res = await session.execute(text("SELECT 1"))
    redis_status = await redis.ping()
    return {"db": bool(res.scalar()), "redis": redis_status}
