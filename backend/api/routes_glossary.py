"""Glossary routes."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.api.schemas import (
    GlossaryCreateRequest,
    GlossaryEntryDetail,
    GlossaryImportResponse,
    GlossaryListResponse,
)
from backend.db.session import get_db
from backend.modules.translator.services.glossary_service import GlossaryEntryData, GlossaryService

router = APIRouter(prefix="/glossary", tags=["glossary"])
glossary_service = GlossaryService()
GLOSSARY_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "glossary"


@router.get("", response_model=GlossaryListResponse)
def list_glossary(
    db: Annotated[Session, Depends(get_db)],
    q: str | None = None,
) -> GlossaryListResponse:
    """List glossary entries with optional search."""
    entries = glossary_service.list_entries(db, q)
    return GlossaryListResponse(
        entries=[GlossaryEntryDetail.model_validate(e) for e in entries],
        query=q or "",
    )


@router.get("/{entry_id}", response_model=GlossaryEntryDetail)
def get_glossary_entry(
    entry_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> GlossaryEntryDetail:
    """Return a single glossary entry."""
    entry = glossary_service.get_entry(db, entry_id)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Glossary entry not found")
    return GlossaryEntryDetail.model_validate(entry)


@router.post("/import", response_model=GlossaryImportResponse)
async def import_glossary(
    db: Annotated[Session, Depends(get_db)],
    glossary_file: Annotated[UploadFile | None, File()] = None,
    file_name: str | None = None,
) -> GlossaryImportResponse:
    """Import glossary CSV data from an upload or data/glossary file name."""
    path = await _resolve_import_file(glossary_file, file_name)
    summary = glossary_service.import_csv_file(db, path)
    return GlossaryImportResponse(
        message=f"Imported {path.name}: {summary.inserted} inserted, {summary.updated} updated",
        file_name=path.name,
        inserted=summary.inserted,
        updated=summary.updated,
        skipped=summary.skipped,
        errors=summary.errors,
    )


@router.post("", response_model=GlossaryEntryDetail, status_code=status.HTTP_201_CREATED)
def create_glossary_entry(
    body: GlossaryCreateRequest,
    db: Annotated[Session, Depends(get_db)],
) -> GlossaryEntryDetail:
    """Create a new glossary entry."""
    status_value = glossary_service.parse_status(body.status)
    data = GlossaryEntryData(
        source_term_en=body.source_term_en.strip(),
        approved_term_zh=body.approved_term_zh.strip(),
        aliases_en=(body.aliases_en or "").strip() or None,
        entity_type=(body.entity_type or "").strip() or None,
        notes=(body.notes or "").strip() or None,
        status=status_value,
    )
    entry = glossary_service.create_entry(db, data)
    return GlossaryEntryDetail.model_validate(entry)


@router.put("/{entry_id}", response_model=GlossaryEntryDetail)
def update_glossary_entry(
    entry_id: int,
    body: GlossaryCreateRequest,
    db: Annotated[Session, Depends(get_db)],
) -> GlossaryEntryDetail:
    """Update an existing glossary entry."""
    status_value = glossary_service.parse_status(body.status)
    data = GlossaryEntryData(
        source_term_en=body.source_term_en.strip(),
        approved_term_zh=body.approved_term_zh.strip(),
        aliases_en=(body.aliases_en or "").strip() or None,
        entity_type=(body.entity_type or "").strip() or None,
        notes=(body.notes or "").strip() or None,
        status=status_value,
    )
    entry = glossary_service.update_entry(db, entry_id, data)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Glossary entry not found")
    return GlossaryEntryDetail.model_validate(entry)


async def _resolve_import_file(
    glossary_file: UploadFile | None,
    file_name: str | None,
) -> Path:
    """Resolve an uploaded or existing data/glossary CSV file."""
    GLOSSARY_DATA_DIR.mkdir(parents=True, exist_ok=True)
    if glossary_file is not None and glossary_file.filename:
        if not glossary_file.filename.lower().endswith(".csv"):
            raise ValueError("Only CSV glossary imports are supported right now.")
        path = GLOSSARY_DATA_DIR / Path(glossary_file.filename).name
        path.write_bytes(await glossary_file.read())
        return path

    clean_name = (file_name or "").strip()
    if not clean_name:
        raise ValueError("Choose a CSV file or enter a file name under data/glossary/.")
    path = GLOSSARY_DATA_DIR / Path(clean_name).name
    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV glossary imports are supported right now.")
    if not path.exists():
        raise ValueError(f"Glossary file not found: {path.name}")
    return path
