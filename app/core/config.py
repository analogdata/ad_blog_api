import logging
import os
from functools import lru_cache
from typing import Any
from datetime import timedelta

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
    db_echo_log: bool = bool(os.getenv("DB_ECHO_LOG", "False") == "True")

    # JWT settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    jwt_refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

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

    @property
    def DATABASE_URL(self) -> str:
        """Return the appropriate database URL based on environment"""
        return self.database_test_url if self.testing else self.database_url

    @property
    def DB_ECHO_LOG(self) -> bool:
        """Return whether to echo SQL logs"""
        return self.db_echo_log

    @property
    def DB_POOL_SIZE(self) -> int:
        """Return database connection pool size"""
        return self.db_pool_size

    @property
    def DB_MAX_OVERFLOW(self) -> int:
        """Return database connection max overflow"""
        return self.db_max_overflow

    @property
    def ACCESS_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        """Return access token expiration time"""
        return timedelta(minutes=self.jwt_access_token_expire_minutes)

    @property
    def REFRESH_TOKEN_EXPIRE_DELTA(self) -> timedelta:
        """Return refresh token expiration time"""
        return timedelta(days=self.jwt_refresh_token_expire_days)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    log.info(f"Loading settings for environment: {settings.environment}")
    return settings


settings = get_settings()
