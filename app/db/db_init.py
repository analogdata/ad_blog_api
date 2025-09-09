"""
Database initialization and connection management for the Blog API.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Create asynchronous engine for PostgreSQL
# Ensure we're using the asynchronous driver by replacing asyncpg with psycopg2
database_url = settings.database_url

# Use asyncpg URL: postgresql+asyncpg://user:pass@host:5432/dbname
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    connect_args={"server_settings": {"timezone": "UTC"}}
)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and yield a database session.
    This function is used as a FastAPI dependency to provide database sessions
    to route handlers.
    """
    async with AsyncSessionLocal() as session:
        yield session
