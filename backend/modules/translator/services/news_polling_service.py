"""Poll official news sources and ingest unseen articles."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select

from backend.core.config import get_settings
from backend.db.models import Article, Job, JobStatus, JobType, SourceType
from backend.db.session import SessionLocal
from backend.modules.translator.services.job_service import JobService
from backend.modules.translator.services.source_parser_service import create_news_client

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PollResult:
    """Summary of one news polling cycle."""

    fetched: int = 0
    created: int = 0
    skipped: int = 0
    failed: int = 0
    errors: tuple[str, ...] = ()


class NewsPollingService:
    """Fetch normalized news articles and queue new ones for translation."""

    def __init__(self, job_service: JobService | None = None) -> None:
        self.job_service = job_service or JobService()

    async def poll_once(self) -> PollResult:
        """Run one poll cycle.

        The implementation uses ``source_url`` as the stable dedupe key.
        Future API clients should continue supplying a stable URL so the
        same dedupe logic works without database schema changes.
        """
        settings = get_settings()
        try:
            client = create_news_client(settings.news_source_type)
        except ValueError as exc:
            logger.warning("News polling disabled: %s", exc)
            return PollResult(errors=(str(exc),))

        articles = []
        try:
            articles = await client.fetch_articles()
        except Exception as exc:
            logger.exception("News source fetch failed")
            return PollResult(failed=1, errors=(str(exc),))
        finally:
            try:
                await client.aclose()
            except Exception:
                logger.exception("Failed to close news source client")

        if not articles:
            return PollResult(fetched=0)

        urls = [article.url for article in articles if article.url]
        existing_urls: set[str] = set()
        if urls:
            with SessionLocal() as db:
                existing_urls = set(
                    db.scalars(
                        select(Article.source_url).where(Article.source_url.in_(urls))
                    )
                )

        created = 0
        skipped = 0
        failed = 0
        errors: list[str] = []

        for article in articles:
            if not article.url:
                failed += 1
                errors.append(f"Article missing URL: {article.title}")
                continue
            if article.url in existing_urls:
                skipped += 1
                continue
            if not article.body.strip():
                failed += 1
                errors.append(f"Article has no body text: {article.title}")
                continue

            try:
                with SessionLocal() as db:
                    stored = Article(
                        source_type=SourceType.official_news,
                        source_url=article.url,
                        source_title=article.title,
                        source_body=article.body,
                        published_at_source=article.published_at,
                    )
                    db.add(stored)
                    db.flush()

                    job = Job(
                        article=stored,
                        job_type=JobType.translate,
                        status=JobStatus.queued,
                        target_language="zh-CN",
                    )
                    db.add(job)
                    db.flush()

                    self.job_service.add_log(
                        db,
                        job,
                        "news_ingest",
                        f"Imported official news article from {article.url}.",
                    )
                    self.job_service.add_log(
                        db,
                        job,
                        "queued",
                        "Queued for automatic translation.",
                    )
                    db.commit()
                    created += 1
            except Exception as exc:
                logger.exception("Failed to ingest news article %s", article.title)
                failed += 1
                errors.append(f"{article.title}: {exc}")

        return PollResult(
            fetched=len(articles),
            created=created,
            skipped=skipped,
            failed=failed,
            errors=tuple(errors),
        )

