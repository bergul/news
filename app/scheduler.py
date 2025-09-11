from __future__ import annotations
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
import pytz
from .config import settings
from .logging_util import get_logger

log = get_logger("scheduler")

def start_scheduler(async_job_fn):
    tz = pytz.timezone(settings.TZ)
    sched = AsyncIOScheduler(timezone=tz)
    cron = settings.SCHEDULE_CRON or "*/15 * * * *"
    trigger = CronTrigger.from_crontab(cron, timezone=tz)
    sched.add_job(async_job_fn, trigger, max_instances=1, coalesce=True, misfire_grace_time=3600)
    sched.start()
    log.info(f"Async scheduler started with cron '{cron}' in TZ={settings.TZ}")
    return sched
