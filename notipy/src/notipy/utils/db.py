import contextlib
from typing import Any, AsyncIterator, Annotated, Optional
import redis.asyncio as redis

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from fastapi import Depends

Base = declarative_base()

# Heavily inspired by https://praciano.com.br/fastapi-and-async-sqlalchemy-20-with-pytest-done-right.html


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(
    "postgresql+asyncpg://root:root@db:5432/notipy", {"echo": True}
)


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session


DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


class RedisManager:
    url: str
    _redis: Optional[redis.Redis]

    def __init__(self, url: str):
        self.url = url
        self._redis = self._initialize()

    def _initialize(self):
        return redis.Redis(
            connection_pool=redis.ConnectionPool.from_url(self.url),
            decode_responses=True,
        )

    def client(self) -> redis.Redis:
        if not self._redis:
            self._redis = self._initialize()
        return self._redis

    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None


redismanager = RedisManager("redis://redis:6379")


async def get_redis():
    yield redismanager.client()


RedisDep = Annotated[redis.Redis, Depends(get_redis)]
