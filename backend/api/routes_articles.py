"""Article routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schemas import (
    ArticleArchiveItem,
    ArticleDetail,
    ArticleListResponse,
    ArticlePollResponse,
    ArticleSummary,
    ArticleTranslationDetail,
    JobSummary,
    ManualSubmissionError,
    ManualSubmissionRequest,
    ManualSubmissionResponse,
)
from backend.db.session import get_db
from backend.modules.translator.services.ingestion_service import IngestionService
from backend.modules.translator.services.news_polling_service import NewsPollingService

router = APIRouter(prefix="/articles", tags=["articles"])
ingestion_service = IngestionService()
news_polling_service = NewsPollingService()


@router.get("", response_model=ArticleListResponse)
def list_articles(
    db: Annotated[Session, Depends(get_db)],
    type: str | None = None,
) -> ArticleListResponse:
    """Return the public article archive, newest first."""
    source_type_map = {"galnet": "official_news", "community_goal": "community_goal"}
    source_type = source_type_map.get(type or "") or (type or None)
    articles = ingestion_service.list_articles(db, source_type=source_type)
    return ArticleListResponse(
        articles=[ArticleArchiveItem.model_validate(a) for a in articles],
        type=type or "",
    )


@router.get("/manual/new")
def manual_submit_form() -> dict[str, object]:
    """Return form metadata for manual submission clients."""
    return {
        "fields": {
            "title": {"type": "string", "required": False},
            "source_url": {"type": "string", "required": False},
            "source_text": {"type": "string", "required": True},
            "target_language": {"type": "string", "default": "zh-CN"},
        }
    }


@router.post(
    "/manual",
    response_model=ManualSubmissionResponse,
    responses={400: {"model": ManualSubmissionError}},
)
def submit_manual_article(
    body: ManualSubmissionRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ManualSubmissionResponse:
    """Validate and persist a manual lore submission."""
    submission, errors = ingestion_service.validate_manual_submission(
        title=body.title,
        source_url=body.source_url,
        source_text=body.source_text,
        target_language=body.target_language,
    )
    if errors or submission is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors[0] if errors else "Validation failed",
        )

    result = ingestion_service.submit_manual_article(db, submission)

    return ManualSubmissionResponse(
        article=ArticleSummary.model_validate(result.article),
        job=JobSummary.model_validate(result.job),
        message=f"Article created. Job #{result.job.id} queued and will translate automatically.",
    )


@router.post("/poll", response_model=ArticlePollResponse)
async def poll_articles() -> ArticlePollResponse:
    """Manually trigger one official news polling and ingestion cycle."""
    result = await news_polling_service.poll_once()
    return ArticlePollResponse(
        fetched=result.fetched,
        created=result.created,
        skipped=result.skipped,
        failed=result.failed,
        errors=list(result.errors),
    )


@router.get("/{identifier}", response_model=ArticleDetail)
def article_detail(
    identifier: str,
    db: Annotated[Session, Depends(get_db)],
) -> ArticleDetail:
    """Return article metadata, source text, and language translations."""
    article = ingestion_service.get_article_by_identifier(db, identifier)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    detail = ArticleDetail.model_validate(article)
    detail.translations = [
        ArticleTranslationDetail(**item)
        for item in ingestion_service.get_translations_for_article(db, article.id)
    ]
    return detail
