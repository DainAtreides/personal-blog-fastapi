import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from app.models import Base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)


async def init_model():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_model())
