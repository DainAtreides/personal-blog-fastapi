import asyncio
import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import event
from models import Base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)


@event.listens_for(engine.sync_engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def init_model():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_model())
