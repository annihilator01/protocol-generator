import functools

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from typing import Any
from typing import Callable
from typing import Coroutine

from core.config import settings

# import all models for create_all function
from .model import Account
from .model import AccountBalanceHistory
from .model import Protocol
from .model import ProtocolToken
from .model import TVLHistory
from .model import Token
from .model import TokenPrice


db_engine: AsyncEngine = create_async_engine(
    settings.db_url,
    # echo=True,
    future=True,
    poolclass=NullPool,
)


async def init_db():
    async with db_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        session: AsyncSession
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def inject_session(
    func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        async with get_session() as session:
            kwargs["session"] = session
            return await func(*args, **kwargs)

    return wrapper
