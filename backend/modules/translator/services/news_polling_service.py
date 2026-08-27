"""Poll GalNet and Community Goal sources and ingest unseen articles."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from backend.core.config import get_settings
from backend.db.models import Article, Job, JobStatus, JobType, SourceType
from backend.db.session import SessionLocal
from backend.modules.translator.services.job_service import JobService
from backend.modules.translator.services.source_parser_service import create_news_client

logger = logging.getLogger(__name__)

_HEADER_RE = re.compile(r"[^a-z0-9]+")


def slugify_title(title: str | None) -> str:
    """Return a lowercase, hyphen-separated header from a title."""
    if not title:
        return "article"
    value = title.lower().replace("'", "").replace("’", "")
    value = _HEADER_RE.sub("-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "article"


def source_prefix(source_type: str) -> str:
    """Return the public URL prefix for an article source type."""
    if source_type in {"official_news", "community"}:
        return "news"
    if source_type == "community_goal":
        return "cg"
    return "manual"


def elite_date_for_slug(published_at):
    if isinstance(published_at, datetime):
        return published_at.date()
    if isinstance(published_at, str):
        raw = published_at.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        return datetime.utcnow().date()
    if published_at is not None:
        return published_at
    return datetime.utcnow().date()


def build_article_slug(source_type: str, published_at, sequence: int) -> str:
    """Build a slug like news-3312-08-24-1 or cg-3312-07-30-1."""
    prefix = source_prefix(source_type)
    day = elite_date_for_slug(published_at)
    return f"{prefix}-{day.year:04d}-{day.month:02d}-{day.day:02d}-{sequence}"


@dataclass(frozen=True)
class PollResult:
    """Summary of one polling cycle."""

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
        settings = get_settings()
        fetched: list = []
        errors: list[str] = []

        galnet = await self._fetch_galnet(settings, errors)
        fetched.extend(galnet)

        try:
            cg_client = create_news_client("community_goal")
        except ValueError as exc:
            errors.append(str(exc))
        else:
            try:
                fetched.extend(await cg_client.fetch_articles())
            except Exception as exc:
                logger.exception("Community Goal fetch failed")
                errors.append(f"Community Goal fetch failed: {exc}")
            finally:
                try:
                    await cg_client.aclose()
                except Exception:
                    logger.exception("Failed to close Community Goal client")

        return await self._ingest(fetched, errors)

    async def _fetch_galnet(self, settings, errors: list[str]):
        source = getattr(settings, "news_source_type", "galnet_api")
        fallback = getattr(settings, "news_fallback_source_type", "community")

        try:
            client = create_news_client(source)
        except ValueError as exc:
            errors.append(str(exc))
            return []

        try:
            return await client.fetch_articles()
        except Exception as exc:
            logger.exception("Primary GalNet fetch failed")
            errors.append(f"Primary GalNet fetch failed: {exc}")
        finally:
            try:
                await client.aclose()
            except Exception:
                logger.exception("Failed to close primary GalNet client")

        if source == fallback:
            return []

        try:
            fallback_client = create_news_client(fallback)
        except ValueError as exc:
            errors.append(str(exc))
            return []

        try:
            articles = await fallback_client.fetch_articles()
            errors.append("Used community scraper fallback for GalNet.")
            return articles
        except Exception as exc:
            logger.exception("Fallback GalNet fetch failed")
            errors.append(f"Fallback GalNet fetch failed: {exc}")
            return []
        finally:
            try:
                await fallback_client.aclose()
            except Exception:
                logger.exception("Failed to close fallback GalNet client")

    async def _ingest(self, articles, errors: list[str]) -> PollResult:
        if not articles:
            return PollResult(errors=tuple(errors))

        created = 0
        skipped = 0
        failed = 0
        for article in articles:
            db_source_type = SourceType.community_goal if article.source_type == "community_goal" else SourceType.official_news
            try:
                with SessionLocal() as db:
                    existing = self._find_existing(db, article)
                    if existing is not None:
                        self._update_existing_if_needed(db, existing, article)
                        db.commit()
                        skipped += 1
                        continue
                    if not article.body.strip():
                        failed += 1
                        errors.append(f"Article has no body text: {article.title}")
                        continue

                    stored = Article(
                        source_type=db_source_type,
                        source_uid=article.uid if not article.legacy_uid else None,
                        legacy_source_uid=article.legacy_uid,
                        article_header=slugify_title(article.title),
                        source_url=article.url,
                        source_title=article.title,
                        source_body=article.body,
                        published_at_source=article.published_at,
                    )
                    db.add(stored)
                    db.flush()
                    stored.slug = self._next_slug(db, stored)
                    db.flush()

                    job = Job(
                        article=stored,
                        job_type=JobType.translate,
                        status=JobStatus.queued,
                        target_language="zh-CN",
                    )
                    db.add(job)
                    db.flush()

                    self.job_service.add_log(db, job, "news_ingest", f"Imported {stored.source_type.value} article from {article.url}.")
                    self.job_service.add_log(db, job, "queued", "Queued for automatic translation.")
                    db.commit()
                    created += 1
            except Exception as exc:
                logger.exception("Failed to ingest article %s", article.title)
                failed += 1
                errors.append(f"{article.title}: {exc}")

        return PollResult(fetched=len(articles), created=created, skipped=skipped, failed=failed, errors=tuple(errors))

    def _find_existing(self, db, article):
        if article.uid:
            by_uid = db.scalar(select(Article).where(Article.source_uid == article.uid))
            if by_uid:
                return by_uid
        if article.legacy_uid:
            by_legacy = db.scalar(select(Article).where(Article.legacy_source_uid == article.legacy_uid))
            if by_legacy:
                return by_legacy
        if article.url:
            by_url = db.scalar(select(Article).where(Article.source_url == article.url))
            if by_url:
                return by_url
        return None

    def _update_existing_if_needed(self, db, existing, article):
        changed = False
        if article.source_type == "galnet" and not article.legacy_uid and not existing.source_uid:
            existing.source_uid = article.uid
            changed = True
        if article.legacy_uid and not existing.legacy_source_uid:
            existing.legacy_source_uid = article.legacy_uid
            changed = True
        if existing.article_header is None:
            existing.article_header = slugify_title(article.title)
            changed = True
        if existing.slug is None:
            existing.slug = self._next_slug(db, existing)
            changed = True
        return changed

    def _next_slug(self, db, article) -> str:
        prefix = source_prefix(article.source_type.value)
        day = elite_date_for_slug(article.published_at_source)
        base = f"{prefix}-{day.year:04d}-{day.month:02d}-{day.day:02d}-"
        existing = db.scalars(select(Article.slug).where(Article.slug.like(f"{base}%"))).all()
        next_seq = 1
        for slug in existing:
            if slug and slug.startswith(base):
                suffix = slug[len(base):]
                if suffix.isdigit():
                    next_seq = max(next_seq, int(suffix) + 1)
        return build_article_slug(article.source_type.value, article.published_at_source, next_seq)
