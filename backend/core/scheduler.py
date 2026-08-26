"""Scheduler setup for background polling jobs."""

import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.core.config import Settings, get_settings
from backend.modules.translator.services.news_polling_service import NewsPollingService

logger = logging.getLogger(__name__)


def _run_news_poll() -> None:
    """Run one news poll cycle from the scheduler worker thread."""
    settings = get_settings()
    if not settings.news_polling_enabled:
        logger.info("Automatic Galnet polling is disabled; skipping scheduled poll.")
        return
    try:
        result = asyncio.run(NewsPollingService().poll_once())
        logger.info(
            "News poll completed: fetched=%s created=%s skipped=%s failed=%s",
            result.fetched,
            result.created,
            result.skipped,
            result.failed,
        )
        for error in result.errors:
            logger.warning("News poll issue: %s", error)
    except Exception:
        logger.exception("News poll failed")


def create_scheduler(settings: Settings) -> BackgroundScheduler:
    """Create the background scheduler with the news poll job registered."""
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.configure(
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
        }
    )
    scheduler.add_job(
        _run_news_poll,
        trigger=IntervalTrigger(minutes=settings.source_poll_interval_minutes),
        id="news_poll",
        name="Poll official news",
        replace_existing=True,
    )
    return scheduler
