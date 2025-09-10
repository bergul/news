from __future__ import annotations
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from .config import settings
from .logging_util import get_logger

log = get_logger("scheduler")

def start_scheduler(job_fn):
    tz = pytz.timezone(settings.TZ)
    sched = BlockingScheduler(timezone=tz)
    cron = settings.SCHEDULE_CRON or "*/15 * * * *"
    trigger = CronTrigger.from_crontab(cron, timezone=tz)
    sched.add_job(job_fn, trigger, max_instances=1, coalesce=True, misfire_grace_time=3600)
    log.info(f"Scheduler started with cron '{cron}' in TZ={settings.TZ}")
    sched.start()
