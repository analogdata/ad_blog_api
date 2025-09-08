from logging.config import fileConfig
import asyncio
import os

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from sqlmodel import SQLModel

from app.core.config import get_settings
from app.db import models  # ensure tables are imported # noqa: F401

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


# Optional: Define a filter to exclude non-public schemas from autogenerate
def include_object(object, name, type_, reflected, compare_to):
    # Exclude system schemas and objects
    if type_ == "schema" and name not in ("public", None):
        return False
    # Include everything else
    return True


def _get_db_url() -> str:
    """Resolve the database URL from settings or environment."""
    try:
        settings = get_settings()
        url = settings.database_url
        if url:
            # ensure async driver
            if "postgresql" in url and "+asyncpg" not in url:
                url = url.replace("postgresql", "postgresql+asyncpg", 1)
            print(f"Using database URL from settings: {url}")
            return url
    except Exception as e:
        print(f"Error getting settings: {e}")

    # Fallback to raw env var
    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        raise RuntimeError(
            "DATABASE_URL is empty. Export it or ensure get_settings() provides it."
        )
    return url


def ensure_extensions_sync(connection):
    """Create PostgreSQL extensions if they don't exist (sync version)"""
    for ext in ("vector", "pg_trgm", "unaccent"):
        connection.execute(text(f"CREATE EXTENSION IF NOT EXISTS {ext}"))
    print("PostgreSQL extensions verified.")


def do_run_migrations(connection):
    """Run migrations with the given connection"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        include_object=include_object,  # Filter out non-public schemas
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = _get_db_url()
    # If you prefer pure offline URL, ensure it's a sync URL (optional).
    url = url.replace("+asyncpg", "")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_server_default=True,
        include_schemas=True,
        include_object=include_object,  # Filter out non-public schemas
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode using a single AsyncEngine."""
    url = _get_db_url()
    connect_args = {}

    # Handle SSL configuration
    if "ssl=require" in url or "ssl=true" in url:
        # Remove from URL and set in connect_args for asyncpg
        url = url.replace("?ssl=require", "").replace("&ssl=require", "")
        url = url.replace("?ssl=true", "").replace("&ssl=true", "")
        connect_args["ssl"] = True
    elif os.getenv("ALEMBIC_FORCE_SSL", "").lower() in {"1", "true", "yes"}:
        connect_args["ssl"] = True

    # Create a single async engine
    engine = create_async_engine(url, connect_args=connect_args, pool_pre_ping=True)

    # We need to start a transaction explicitly for AsyncEngine
    async with engine.begin() as conn:
        # Run both extension creation and migrations using run_sync
        await conn.run_sync(ensure_extensions_sync)
        await conn.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
