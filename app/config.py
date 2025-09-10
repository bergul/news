from __future__ import annotations
import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        # asyncpg avoids Windows ProactorEventLoop issues
        "postgresql+asyncpg://postgres:Q1w2e34@127.0.0.1:5432/newsdb",
    )
    SCHEDULE_CRON: str = os.getenv("SCHEDULE_CRON", "*/15 * * * *")  # every 15 minutes
    TZ: str = os.getenv("TZ", "Europe/Istanbul")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    API_KEYS: str = os.getenv("API_KEYS", "")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    WEBHOOK_URLS: str = os.getenv("WEBHOOK_URLS", "")

    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "200"))
    RATE_LIMIT_KEY_STRATEGY: str = os.getenv("RATE_LIMIT_KEY_STRATEGY", "api_key_or_ip")

    REQUEST_LOG_HEADERS: str = os.getenv("REQUEST_LOG_HEADERS", "x-api-key,user-agent")
    REQUEST_LOG_QUERY: bool = os.getenv("REQUEST_LOG_QUERY", "true").lower() == "true"
    REQUEST_LOG_BODY: bool = os.getenv("REQUEST_LOG_BODY", "false").lower() == "true"

    def _normalize_db_url(self) -> None:
        try:
            import sys
            if not sys.platform.startswith("win"):
                return
            url = self.DATABASE_URL or ""
            if "+asyncpg" in url:
                return
            if url.startswith("postgresql+"):
                self.DATABASE_URL = "postgresql+asyncpg://" + url.split("://", 1)[1]
            elif url.startswith("postgres://") or url.startswith("postgresql://"):
                self.DATABASE_URL = "postgresql+asyncpg://" + url.split("://", 1)[1]
        except Exception:
            pass

    def model_post_init(self, __context):
        self._normalize_db_url()

settings = Settings()
