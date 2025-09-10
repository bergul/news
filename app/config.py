from __future__ import annotations
import os
from pydantic import BaseModel
from typing import Optional

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./news.db")
    SCHEDULE_CRON: str = os.getenv("SCHEDULE_CRON", "*/15 * * * *")  # every 15 minutes
    TZ: str = os.getenv("TZ", "Europe/Istanbul")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    API_KEYS: str = os.getenv("API_KEYS", "")  # virgülle ayrılmış anahtarlar: key1,key2
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")  # '*' veya virgülle ayrılmış kökenler
    WEBHOOK_URLS: str = os.getenv("WEBHOOK_URLS", "")  # virgülle ayrılmış endpoint listesi

    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "120"))  # dakika başına istek
    RATE_LIMIT_BURST: int = int(os.getenv("RATE_LIMIT_BURST", "200"))            # ani patlama toleransı
    RATE_LIMIT_KEY_STRATEGY: str = os.getenv("RATE_LIMIT_KEY_STRATEGY", "api_key_or_ip")  # api_key | ip | api_key_or_ip

    REQUEST_LOG_HEADERS: str = os.getenv("REQUEST_LOG_HEADERS", "x-api-key,user-agent")
    REQUEST_LOG_QUERY: bool = os.getenv("REQUEST_LOG_QUERY", "true").lower() == "true"
    REQUEST_LOG_BODY: bool = os.getenv("REQUEST_LOG_BODY", "false").lower() == "true"   # hassas veri için varsayılan kapalı

settings = Settings()
