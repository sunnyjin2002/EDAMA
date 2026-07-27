"""EDAMA REST API entrypoint."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.api.routes_articles import router as articles_router
from backend.api.routes_glossary import router as glossary_router
from backend.api.routes_jobs import router as jobs_router
from backend.api.routes_publish import router as publish_router
from backend.api.routes_settings import router as settings_router
from backend.api.routes_translation_memory import router as translation_memory_router
from backend.api.schemas import DashboardResponse, HealthResponse, JobSummary
from backend.core.config import get_settings
from backend.core.logging import configure_logging
from backend.core.scheduler import create_scheduler
from backend.db.session import SessionLocal, create_database_tables, get_db
from backend.modules.translator.services.job_service import JobService
from backend.modules.translator.services.glossary_service import GlossaryService

settings = get_settings()
job_service = JobService()
glossary_service = GlossaryService()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure process-level resources for the application lifetime."""
    configure_logging(settings.log_level)
    create_database_tables()

    # Load glossary CSV files at startup
    with SessionLocal() as db:
        glossary_service.reload_glossary_from_files(db)

    scheduler = create_scheduler(settings)
    app.state.scheduler = scheduler
    scheduler.start(paused=True)
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3302"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(articles_router)
    app.include_router(jobs_router)
    app.include_router(glossary_router)
    app.include_router(translation_memory_router)
    app.include_router(publish_router)
    app.include_router(settings_router)

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        """Return a lightweight health check response."""
        return HealthResponse(status="ok")

    @app.get("/", response_model=DashboardResponse)
    def dashboard(db: Annotated[Session, Depends(get_db)]) -> DashboardResponse:
        """Return dashboard with recent jobs."""
        recent_jobs = job_service.list_recent_jobs(db)
        return DashboardResponse(
            app_name=settings.app_name,
            recent_jobs=[JobSummary.model_validate(j) for j in recent_jobs],
        )

    @app.post("/glossary/reload", tags=["glossary"])
    def reload_glossary(db: Annotated[Session, Depends(get_db)]) -> dict[str, object]:
        """Reload all glossary CSV files from data/glossary/ into the database."""
        summary = glossary_service.reload_glossary_from_files(db)
        return {
            "message": "Glossary reloaded",
            "inserted": summary.inserted,
            "updated": summary.updated,
            "skipped": summary.skipped,
            "errors": list(summary.errors),
        }

    return app


app = create_app()
