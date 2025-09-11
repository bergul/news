from __future__ import annotations
import argparse
from datetime import datetime
from .config import settings
from .logging_util import get_logger
from .db import SessionLocal, engine
from .ingest import ensure_schema, save_items
from .loader import load_sources
from .scheduler import start_scheduler
import asyncio

log = get_logger("main")

_schema_done = False

async def run_once():
    global _schema_done
    if not _schema_done:
        await ensure_schema(engine)
        _schema_done = True
    sources = load_sources("config/sources.yml")
    total = 0
    async with SessionLocal() as s:
        for src in sources:
            try:
                items = list(src.fetch())
                inserted = await save_items(s, items)
                total += inserted
                log.info(f"[{src.name}] fetched={len(items)} inserted={inserted}")
            except Exception as e:
                log.exception(f"Source error: {src.name}: {e}")
    log.info(f"Done. Inserted total={total}")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single ingestion and exit")
    args = parser.parse_args()
    if args.once:
        await run_once()
    else:
        def job():
            asyncio.run(run_once())
        start_scheduler(job)

if __name__ == "__main__":
    asyncio.run(main())
