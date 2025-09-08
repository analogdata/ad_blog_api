import logging
import os
from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "local")
    testing: bool = bool(os.getenv("TESTING", False) == "True")
    debug: bool = bool(os.getenv("DEBUG", "True") == "True")

    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "")
    database_test_url: str = os.getenv("DATABASE_TEST_URL", "")
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))

    # Strip quotes from database URLs if present
    def _process_db_url(self, url: str) -> str:
        if not url:
            return url
        # Remove quotes if present
        if url.startswith('"') and url.endswith('"'):
            return url[1:-1]
        if url.startswith("'") and url.endswith("'"):
            return url[1:-1]
        return url

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.database_url = self._process_db_url(self.database_url)
        self.database_test_url = self._process_db_url(self.database_test_url)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    log.info(f"Loading settings:\n{settings}\n")
    return settings
