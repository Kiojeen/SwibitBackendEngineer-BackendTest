import os
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.user import User

DATABASE_URL = os.getenv("DATABASE_URL")

_engine = create_async_engine(DATABASE_URL)
_async_session_maker = async_sessionmaker(_engine, expire_on_commit=False)

SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "+psycopg")
_sync_engine = create_engine(SYNC_DATABASE_URL)
_sync_session_maker = sessionmaker(_sync_engine)


def get_sync_session() -> Session:
    return _sync_session_maker()


async def create_db_and_tables():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
