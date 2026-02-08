"""
Database connection and session management.
Provides async SQLAlchemy engine and session factory for Neon PostgreSQL.
Uses lazy initialization to avoid creating engine at import time.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from config import settings


# Lazy initialization - engine and session maker created on first use
_engine = None
_async_session_maker = None


def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            future=True,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
    return _engine


def get_async_session_maker():
    """Get or create the async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_maker


# For backward compatibility - this is now a function call, not module-level initialization
async_session_maker = get_async_session_maker


async def get_session() -> AsyncSession:
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    async with get_async_session_maker()() as session:
        yield session


async def init_db():
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
