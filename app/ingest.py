from __future__ import annotations
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from .models import News
from .utils import tag_by_keywords, join_tags
from .logging_util import get_logger
from .webhook import notify_news
import asyncio

log = get_logger("ingest")

async def ensure_schema(engine):
    from .db import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_items(session: AsyncSession, items) -> int:
    inserted = 0
    inserted_payloads = []
    for it in items:
        result = await session.execute(select(News).where(News.url == it.url))
        existing = result.scalar_one_or_none()

        tags = join_tags(tag_by_keywords(it.title + " " + it.summary, it.language))

        if existing:
            if it.published_at and existing.published_at and it.published_at > existing.published_at:
                existing.title = it.title or existing.title
                existing.summary = it.summary or existing.summary
                existing.content = it.content or existing.content
                existing.published_at = it.published_at
                existing.tags = tags or existing.tags
                existing.language = it.language or existing.language
                existing.source_name = it.source_name or existing.source_name
                # merge raw
                try:
                    merged = dict(existing.raw or {})
                    merged.update(it.raw or {})
                    existing.raw = merged
                except Exception:
                    existing.raw = it.raw or existing.raw
                log.info(f"Updated: {existing.title}")
            continue
        news = News(
            source_name=it.source_name,
            title=it.title,
            url=it.url,
            published_at=it.published_at or datetime.now(tz=timezone.utc),
            summary=it.summary,
            content=it.content,
            language=it.language,
            tags=tags,
            raw=it.raw,
        )
        session.add(news)

        inserted += 1
        try:
            inserted_payloads.append({
                "id": None,
                "source_name": news.source_name,
                "title": news.title,
                "url": news.url,
                "published_at": news.published_at.isoformat() if news.published_at else None,
                "summary": news.summary,
                "content": news.content,
                "language": news.language,
                "tags": news.tags,
            })
        except Exception:
            pass

    await session.commit()
    # Send webhooks outside the transaction
    try:
        if inserted_payloads:
            notify_news(inserted_payloads)
    except Exception:
        pass
    return inserted
