"""Translation memory routes."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend.api.schemas import (
    TranslationMemoryEntryDetail,
    TranslationMemoryImportResponse,
    TranslationMemoryListResponse,
)
from backend.db.session import get_db
from backend.modules.translator.services.translation_memory_service import TranslationMemoryService

router = APIRouter(prefix="/translation-memory", tags=["translation-memory"])
translation_memory_service = TranslationMemoryService()
TRANSLATION_MEMORY_DIR = (
    Path(__file__).resolve().parents[2] / "data" / "references" / "translation_memory"
)


@router.get("", response_model=TranslationMemoryListResponse)
def list_translation_memory(
    db: Annotated[Session, Depends(get_db)],
    q: str | None = None,
) -> TranslationMemoryListResponse:
    """List translation memory entries with optional search."""
    entries = translation_memory_service.list_entries(db, q)
    matches = translation_memory_service.retrieve_similar_passages(db, q, limit=10) if q else []
    return TranslationMemoryListResponse(
        entries=[TranslationMemoryEntryDetail.model_validate(e) for e in entries],
        matches=[TranslationMemoryEntryDetail.model_validate(m) for m in matches],
        query=q or "",
    )


@router.post("/import", response_model=TranslationMemoryImportResponse)
async def import_translation_memory(
    db: Annotated[Session, Depends(get_db)],
    memory_file: Annotated[UploadFile | None, File()] = None,
    file_name: str | None = None,
) -> TranslationMemoryImportResponse:
    """Import translation memory CSV data from upload or reference directory."""
    path = await _resolve_import_file(memory_file, file_name)
    summary = translation_memory_service.import_csv_file(db, path)
    return TranslationMemoryImportResponse(
        message=f"Imported {path.name}: {summary.inserted} inserted, {summary.updated} updated",
        file_name=path.name,
        inserted=summary.inserted,
        updated=summary.updated,
        skipped=summary.skipped,
        errors=summary.errors,
    )


async def _resolve_import_file(memory_file: UploadFile | None, file_name: str | None) -> Path:
    """Resolve an uploaded or existing translation memory CSV file."""
    TRANSLATION_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if memory_file is not None and memory_file.filename:
        if not memory_file.filename.lower().endswith(".csv"):
            raise ValueError("Only CSV translation memory imports are supported right now.")
        path = TRANSLATION_MEMORY_DIR / Path(memory_file.filename).name
        path.write_bytes(await memory_file.read())
        return path

    clean_name = (file_name or "").strip()
    if not clean_name:
        raise ValueError(
            "Choose a CSV file or enter a file name under data/references/translation_memory/."
        )
    path = TRANSLATION_MEMORY_DIR / Path(clean_name).name
    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV translation memory imports are supported right now.")
    if not path.exists():
        raise ValueError(f"Translation memory file not found: {path.name}")
    return path
