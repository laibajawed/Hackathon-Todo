"""
Database connection and session management.
Provides async SQLAlchemy engine and session factory for Neon PostgreSQL.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from config import settings


# Lazy initialization for serverless environments
_engine = None
_async_session_maker = None


def get_engine():
    """Get or create the database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        # Optimized for serverless: smaller pool, no pre-ping
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.ENVIRONMENT == "development",
            future=True,
            pool_pre_ping=False,  # Disabled for serverless
            pool_size=1,  # Minimal pool for serverless
            max_overflow=0,  # No overflow for serverless
            pool_recycle=300,  # Recycle connections after 5 minutes
        )
    return _engine


def get_session_maker():
    """Get or create the session maker (lazy initialization)."""
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


# For backward compatibility
engine = property(lambda self: get_engine())
async_session_maker = property(lambda self: get_session_maker())


async def get_session() -> AsyncSession:
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        yield session


async def init_db():
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
