from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqladmin import Admin
from sqlalchemy import text
from contextlib import asynccontextmanager

from src.admin.auth import AdminAuth
from src.admin.views import UserAdmin
from src.core.config import settings
from src.core.database import SessionDep, engine
from src.core.redis import RedisDep, redis_client
from src.core.exceptions import AppError

from src.auth.router import router as user_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_client.aclose()
    await engine.dispose()


app = FastAPI(title="dp-place", lifespan=lifespan)
app.include_router(user_router)

admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=settings.ADMIN_SESSION_SECRET), title="DP-Place Admin")
admin.add_view(UserAdmin)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.get("/health")
async def get_database_health(session: SessionDep, redis: RedisDep):
    res = await session.execute(text("SELECT 1"))
    redis_status = await redis.ping()
    res = "✅" if res else "❌"
    redis_status = "✅" if redis_status else "❌"
    return {"db": res, "redis": redis_status}
