import asyncio
import sys
from sqlalchemy import update

from src.auth.models import User, UserRole
from src.core.database import async_session_maker

async def main(email: str) -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            update(User).where(User.email==email.lower()).values(role=UserRole.ADMIN)
        )
        await session.commit()
        print("🔼 Updated role to ADMIN:")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("➡️ Use: uv run python -m scripts.promotion_to_admin <email>")
    asyncio.run(main(sys.argv[1]))