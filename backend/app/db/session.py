from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return the singleton async engine, creating it on first call.

    Lazily initialized so models can be imported without a database URL
    being configured (important for Alembic env.py and tests).
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the singleton async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an AsyncSession, closes after the request.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with get_session_factory()() as session:
        try:
            yield session
        finally:
            await session.close()
