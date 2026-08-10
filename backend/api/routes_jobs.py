"""Job routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schemas import JobDetail, JobSummary
from backend.db.session import get_db
from backend.modules.translator.services.job_service import JobService
from backend.modules.translator.services.translation_service import TranslationService
from backend.modules.translator.services.review_service import ReviewService
from backend.modules.translator.services.tagging_service import TaggingService

router = APIRouter(prefix="/jobs", tags=["jobs"])
job_service = JobService()
translation_service = TranslationService()
review_service = ReviewService()
tagging_service = TaggingService()


@router.get("", response_model=list[JobSummary])
def list_jobs(db: Annotated[Session, Depends(get_db)]) -> list[JobSummary]:
    """Return all jobs ordered newest first."""
    jobs = job_service.list_jobs(db)
    return [JobSummary.model_validate(j) for j in jobs]


@router.get("/{job_id}", response_model=JobDetail)
def job_detail(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> JobDetail:
    """Return job status, article metadata, and logs."""
    job = job_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    detail = JobDetail.model_validate(job)
    _populate_translation(detail, job)
    return detail


@router.post("/{job_id}/tags", response_model=JobDetail)
async def tag_job(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> JobDetail:
    """Run tag extraction on a job's article."""
    job = await tagging_service.extract_tags(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag extraction not available",
        )
    detail = JobDetail.model_validate(job)
    _populate_translation(detail, job)
    return detail


@router.post("/{job_id}/review", response_model=JobDetail)
async def review_job(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> JobDetail:
    """Run translation review on a job."""
    job = await review_service.review_translation(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review not available (disabled, no translation, or not found)",
        )
    detail = JobDetail.model_validate(job)
    _populate_translation(detail, job)
    return detail


@router.post("/{job_id}/translate", response_model=JobDetail)
async def translate_job(
    job_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> JobDetail:
    """Run first-pass translation on a job."""
    job = await translation_service.translate_article(db, job_id)
    detail = JobDetail.model_validate(job)
    _populate_translation(detail, job)
    return detail


def _populate_translation(detail: JobDetail, job: object) -> None:
    """Copy translation fields from the first translation record if present."""
    translations = getattr(job, "translations", []) or []
    if translations:
        t = translations[0]
        detail.translated_title = t.translated_title
        detail.translated_body = t.translated_body
        detail.reviewed_title = t.reviewed_title
        detail.reviewed_body = t.reviewed_body
        detail.review_notes = t.review_notes
        detail.confidence_score = t.confidence_score
    # Populate tags from article
    article = getattr(job, "article", None)
    if article:
        tag_links = getattr(article, "tag_links", []) or []
        detail.tags = sorted(
            link.tag.name for link in tag_links if getattr(link, "tag", None)
        )
