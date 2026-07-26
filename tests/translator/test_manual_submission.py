"""Manual submission service tests."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.db import models  # noqa: F401
from backend.db.base import Base
from backend.db.models import JobStatus, JobType, SourceType
from backend.modules.translator.services.ingestion_service import IngestionService, ManualSubmissionData


def test_manual_submission_creates_article_job_and_logs() -> None:
    """Manual submission persists the expected draft-oriented records."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with session_factory() as db:
        result = IngestionService().submit_manual_article(
            db,
            ManualSubmissionData(
                title="Achenar archive fragment",
                source_url=None,
                source_text="Lore source text",
                target_language="zh-CN",
            ),
        )

        assert result.article.source_type == SourceType.manual_lore
        assert result.job.job_type == JobType.manual_submission
        assert result.job.status == JobStatus.queued
        assert len(result.job.logs) == 2
