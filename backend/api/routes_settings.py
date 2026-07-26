"""Settings routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
def get_settings() -> dict[str, object]:
    """Return settings placeholder."""
    return {"status": "ok", "message": "Settings not yet configurable via API"}
