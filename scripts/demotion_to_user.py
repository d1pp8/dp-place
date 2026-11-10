import asyncio
import sys
from sqlalchemy import update

from src.auth.models import User, UserRole
from src.core.database import async_session_maker

async def main(email: str) -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            update(User).where(User.email==email.lower()).values(role=UserRole.USER)
        )
    await session.commit()
    print("🔽 Updated role to user")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("➡️ Use: uv run python -m scripts.demotion_to_user <email>")
    asyncio.run(main(sys.argv[1]))