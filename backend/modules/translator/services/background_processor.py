"""Background job processor — polls for queued jobs and retries failed ones."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.core.config import get_settings
from backend.db.models import Job, JobStatus
from backend.db.session import SessionLocal
from backend.modules.translator.services.translation_service import TranslationService

logger = logging.getLogger(__name__)


class BackgroundProcessor:
    """Periodically scans for jobs that need processing.

    - Queued jobs are translated.
    - Failed jobs retry up to max_retries times.
    - Stuck running jobs are timed out.

    Each job uses its own DB session to avoid long write locks.
    """

    def __init__(self) -> None:
        self._translation = TranslationService()
        self._stop = False

    async def run_loop(self, poll_interval: float = 2.0) -> None:
        logger.info("Background processor started")
        while not self._stop:
            try:
                await self._tick()
            except Exception:
                logger.exception("Background processor error")
            await asyncio.sleep(poll_interval)
        logger.info("Background processor stopped")

    def stop(self) -> None:
        self._stop = True

    # -- internals --------------------------------------------------

    async def _tick(self) -> None:
        settings = get_settings()
        timeout = settings.translation_timeout_seconds
        max_retries = settings.translation_max_retries

        with SessionLocal() as db:
            self._timeout_stuck_jobs(db, timeout)

        await self._drain_queued(timeout)
        await self._drain_failed(timeout, max_retries)

    async def _drain_queued(self, timeout: int) -> None:
        with SessionLocal() as db:
            ids = [r[0] for r in db.execute(
                select(Job.id).where(Job.status == JobStatus.queued)
            )]
        for jid in ids:
            with SessionLocal() as db:
                job = db.get(Job, jid)
                if job is None or job.status != JobStatus.queued:
                    continue
                logger.info("Processing queued job #%d", jid)
                try:
                    await asyncio.wait_for(
                        self._translation.translate_article(db, jid),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    job.status = JobStatus.failed
                    job.error_message = f"Timed out after {timeout}s"
                    job.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    db.commit()
                except Exception:
                    logger.exception("Job #%d failed", jid)
                    db.rollback()

    async def _drain_failed(self, timeout: int, max_retries: int) -> None:
        with SessionLocal() as db:
            ids = [r[0] for r in db.execute(
                select(Job.id).where(
                    Job.status == JobStatus.failed,
                    Job.retry_count < max_retries,
                )
            )]
        for jid in ids:
            with SessionLocal() as db:
                job = db.get(Job, jid)
                if job is None or job.status != JobStatus.failed:
                    continue
                job.status = JobStatus.queued
                job.retry_count += 1
                db.commit()
                logger.info("Retrying job #%d (attempt %d/%d)", jid, job.retry_count, max_retries)
            with SessionLocal() as db:
                try:
                    await asyncio.wait_for(
                        self._translation.translate_article(db, jid),
                        timeout=timeout,
                    )
                except asyncio.TimeoutError:
                    job2 = db.get(Job, jid)
                    if job2:
                        job2.status = JobStatus.failed
                        job2.error_message = (
                            f"Retry #{job2.retry_count} timed out after {timeout}s"
                        )
                        job2.finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
                        db.commit()
                except Exception:
                    logger.exception("Job #%d retry failed", jid)
                    db.rollback()

    @staticmethod
    def _timeout_stuck_jobs(db: Session, timeout_seconds: int) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        stmt = (
            select(Job)
            .where(Job.status == JobStatus.running)
            .options(selectinload(Job.article), selectinload(Job.logs))
        )
        for job in db.scalars(stmt):
            if job.started_at is None:
                continue
            elapsed = (now - job.started_at).total_seconds()
            if elapsed > timeout_seconds:
                job.status = JobStatus.failed
                job.error_message = (
                    f"Timed out after {int(elapsed)}s (limit: {timeout_seconds}s)"
                )
                job.finished_at = now
                logger.warning("Job #%d timed out after %ds", job.id, int(elapsed))
        db.commit()
