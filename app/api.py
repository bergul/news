from __future__ import annotations
from typing import List, Optional
from fastapi import FastAPI, Query, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from datetime import datetime
import yaml

from .db import SessionLocal, engine
from .models import News
from .ingest import ensure_schema
from .config import settings
from .middleware import RateLimiter, RequestLogger

app = FastAPI(title="Commodities News API", version="1.0.0")
# Request logging & rate limiting
app.add_middleware(RequestLogger)
app.add_middleware(RateLimiter)

# CORS
_origins = [o.strip() for o in (settings.CORS_ORIGINS or "*").split(",")] if settings.CORS_ORIGINS else ["*"]
if _origins == ["*"]:
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
else:
    app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class NewsOut(BaseModel):
    id: int
    source_name: str
    title: str
    url: str
    published_at: datetime
    summary: str
    content: str
    language: str
    tags: str

    class Config:
        from_attributes = True

def _session():
    return SessionLocal()


def get_api_keys():
    raw = (settings.API_KEYS or "").strip()
    return [k.strip() for k in raw.split(",") if k.strip()]

def api_key_auth(x_api_key: str = Header(default=None, alias="x-api-key")):
    keys = get_api_keys()
    if keys and (x_api_key not in keys):
        raise HTTPException(401, "Invalid or missing API key")
    return True


@app.on_event("startup")
def startup():
    ensure_schema(engine)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/sources", dependencies=[Depends(api_key_auth)])
def sources():
    try:
        with open("config/sources.yml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        if isinstance(cfg, list):
            return {"sources": cfg}
        return {"sources": cfg.get("sources", [])}
    except Exception as e:
        raise HTTPException(500, f"Could not read sources.yml: {e}")

@app.get("/news", response_model=List[NewsOut])
def list_news(
    q: Optional[str] = Query(None, description="Full-text query over title/summary/content (simple LIKE search)"),
    source: Optional[str] = Query(None, description="Exact source_name"),
    lang: Optional[str] = Query(None, description="Language code filter (e.g., tr/en)"),
    tag: Optional[str] = Query(None, description="Contains tag text"),
    published_from: Optional[datetime] = Query(None, description="ISO date lower bound (inclusive)"),
    published_to: Optional[datetime] = Query(None, description="ISO date upper bound (exclusive)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    with _session() as s:
        stmt = select(News)
        conds = []
        if source:
            conds.append(News.source_name == source)
        if lang:
            conds.append(News.language == lang)
        if tag:
            conds.append(News.tags.ilike(f"%{tag}%"))
        if published_from:
            conds.append(News.published_at >= published_from)
        if published_to:
            conds.append(News.published_at < published_to)
        if q:
            like = f"%{q}%"
            conds.append(and_( (News.title.ilike(like)) | (News.summary.ilike(like)) | (News.content.ilike(like)) ))
        if conds:
            from sqlalchemy import and_ as _and
            stmt = stmt.where(_and(*conds))
        if order.lower() == "desc":
            stmt = stmt.order_by(News.published_at.desc(), News.id.desc())
        else:
            stmt = stmt.order_by(News.published_at.asc(), News.id.asc())
        stmt = stmt.limit(limit).offset(offset)
        rows = s.execute(stmt).scalars().all()
        return [NewsOut.model_validate(r) for r in rows]

@app.get("/news/count")
def count_news(
    q: Optional[str] = None,
    source: Optional[str] = None,
    lang: Optional[str] = None,
    tag: Optional[str] = None,
    published_from: Optional[datetime] = None,
    published_to: Optional[datetime] = None,
):
    with _session() as s:
        stmt = select(func.count(News.id))
        conds = []
        if source:
            conds.append(News.source_name == source)
        if lang:
            conds.append(News.language == lang)
        if tag:
            conds.append(News.tags.ilike(f"%{tag}%"))
        if published_from:
            conds.append(News.published_at >= published_from)
        if published_to:
            conds.append(News.published_at < published_to)
        if q:
            like = f"%{q}%"
            from sqlalchemy import or_
            conds.append(or_(News.title.ilike(like), News.summary.ilike(like), News.content.ilike(like)))
        if conds:
            from sqlalchemy import and_ as _and
            stmt = stmt.where(_and(*conds))
        total = s.execute(stmt).scalar_one()
        return {"count": int(total)}
