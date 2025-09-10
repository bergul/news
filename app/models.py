from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .db import Base

class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String(200), index=True)
    title: Mapped[str] = mapped_column(String(1024), index=True)
    url: Mapped[str] = mapped_column(String(2048), unique=False, index=True)
    published_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    language: Mapped[str] = mapped_column(String(8), default="")
    tags: Mapped[str] = mapped_column(String(512), default="")  # comma separated
    fetched_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    raw: Mapped[dict] = mapped_column(JSONB().with_variant(Text, "sqlite"), default={})  # JSONB for PG, Text for SQLite
