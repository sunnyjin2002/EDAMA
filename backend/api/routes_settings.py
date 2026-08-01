"""Settings routes — read and update application settings."""

from fastapi import APIRouter, HTTPException, status

from backend.api.schemas import SettingsResponse, SettingsUpdateRequest
from backend.core.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


def _build_response() -> SettingsResponse:
    s = get_settings()
    return SettingsResponse(
        translation_provider=s.translation_provider,
        translation_model=s.translation_model,
        review_provider=s.review_provider,
        review_model=s.review_model,
        tagging_provider=s.tagging_provider,
        tagging_model=s.tagging_model,
        source_poll_url=s.source_poll_url,
        source_poll_interval_minutes=s.source_poll_interval_minutes,
        auto_publish_official_news=s.auto_publish_official_news,
    )


@router.get("", response_model=SettingsResponse)
def get_settings_endpoint() -> SettingsResponse:
    """Return current application settings."""
    return _build_response()


@router.post("", response_model=SettingsResponse)
def update_settings(body: SettingsUpdateRequest) -> SettingsResponse:
    """Update application settings in-memory."""
    s = get_settings()
    changed = False
    for field in (
        "translation_provider",
        "translation_model",
        "review_provider",
        "review_model",
        "tagging_provider",
        "tagging_model",
        "source_poll_url",
        "source_poll_interval_minutes",
        "auto_publish_official_news",
    ):
        val = getattr(body, field)
        if val is not None:
            setattr(s, field, val)
            changed = True
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )
    return _build_response()
