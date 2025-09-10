from __future__ import annotations
import argparse
from datetime import datetime
from .config import settings
from .logging_util import get_logger
from .db import SessionLocal, engine
from .ingest import ensure_schema, save_items
from .loader import load_sources
from .scheduler import start_scheduler

log = get_logger("main")

def run_once():
    ensure_schema(engine)
    sources = load_sources("config/sources.yml")
    total = 0
    with SessionLocal() as s:
        for src in sources:
            try:
                items = list(src.fetch())
                inserted = save_items(s, items)
                total += inserted
                log.info(f"[{src.name}] fetched={len(items)} inserted={inserted}")
            except Exception as e:
                log.exception(f"Source error: {src.name}: {e}")
    log.info(f"Done. Inserted total={total}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run a single ingestion and exit")
    args = parser.parse_args()
    if args.once:
        run_once()
    else:
        def job():
            run_once()
        start_scheduler(job)

if __name__ == "__main__":
    main()
