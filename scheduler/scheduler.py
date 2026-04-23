from typing import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

_scheduler = BackgroundScheduler(timezone="Europe/Amsterdam")


def start(run_pipeline_fn: Callable) -> None:
    _scheduler.add_job(
        run_pipeline_fn,
        trigger=CronTrigger(hour=8, minute=30),
        id="daily_scrape",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    _scheduler.start()


def stop() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
