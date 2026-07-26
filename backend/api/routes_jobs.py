"""Job routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schemas import JobDetail, JobSummary
from backend.db.session import get_db
from backend.modules.translator.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])
job_service = JobService()


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
    return JobDetail.model_validate(job)
