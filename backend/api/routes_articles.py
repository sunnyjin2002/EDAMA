"""Article routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schemas import (
    ArticleDetail,
    ArticleSummary,
    JobSummary,
    ManualSubmissionError,
    ManualSubmissionRequest,
    ManualSubmissionResponse,
)
from backend.db.session import get_db
from backend.modules.translator.services.ingestion_service import IngestionService

router = APIRouter(prefix="/articles", tags=["articles"])
ingestion_service = IngestionService()


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


@router.get("/{article_id}", response_model=ArticleDetail)
def article_detail(
    article_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ArticleDetail:
    """Return article metadata, source text, and related jobs."""
    article = ingestion_service.get_article(db, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return ArticleDetail.model_validate(article)
