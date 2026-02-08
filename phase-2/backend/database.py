"""
Database connection and session management.
Provides async SQLAlchemy engine and session factory for Neon PostgreSQL.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from config import settings


# Create async engine for Neon PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # Log SQL queries in development
    future=True,
    pool_pre_ping=True,  # Verify connections before use
    pool_size=10,  # Max 10 connections
    max_overflow=20,  # Allow 20 overflow connections
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    """
    Dependency function to get database session.
    Yields a session and ensures it's closed after use.
    """
    async with async_session_maker() as session:
        yield session


async def init_db():
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
