from typing import Union, Callable, Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession,
    AsyncEngine,
    AsyncConnection,
)

from src.core import app_settings


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def create_sessionmaker(
    bind_engine: Union[AsyncEngine, AsyncConnection],
) -> Callable[..., async_sessionmaker]:
    return async_sessionmaker(
        bind=bind_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


engine = create_async_engine(str(app_settings.postgres_dsn))

async_session = create_sessionmaker(engine)

db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
