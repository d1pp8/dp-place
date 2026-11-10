from fastapi import FastAPI
from sqlalchemy import text
from sqladmin import Admin

from src.admin.auth import AdminAuth
from src.core.config import settings
from src.core.database import SessionDep, engine
from src.admin.views import UserAdmin
from src.core.redis import RedisDep

from src.auth.router import router as user_router

app = FastAPI(title="dp-place")
app.include_router(user_router)

admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=settings.ADMIN_SESSION_SECRET), title="DP-Place Admin")
admin.add_view(UserAdmin)


@app.get("/health")
async def get_database_health(session: SessionDep, redis: RedisDep):
    res = await session.execute(text("SELECT 1"))
    redis_status = await redis.ping()
    res = "✅" if res else "❌"
    redis_status = "✅" if redis_status else "❌"
    return {"db": res, "redis": redis_status}
