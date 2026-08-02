"""Settings routes — read and update application settings, persisted to .env."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from backend.api.schemas import SettingsResponse, SettingsUpdateRequest
from backend.core.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])

ENV_PATH = Path(".env")  # resolved relative to CWD (repo root)


def _env_key(field: str) -> str:
    return field.upper()


def _write_env_file(updates: dict[str, str]) -> None:
    """Persist changed settings to the .env file.

    Existing lines for matching keys are replaced in-place.
    New keys are appended at the end of the file.
    """
    if not ENV_PATH.exists():
        lines: list[str] = []
    else:
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    updated_keys: set[str] = set()
    result: list[str] = []

    for line in lines:
        stripped = line.strip()
        # Preserve blank lines and comments
        if not stripped or stripped.startswith("#"):
            result.append(line)
            continue
        # Try to match KEY=VALUE lines
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            upper_key = key.upper()
            if upper_key in updates:
                result.append(f"{upper_key}={updates[upper_key]}")
                updated_keys.add(upper_key)
                continue
        result.append(line)

    # Append any keys not already present
    for key, value in updates.items():
        if key not in updated_keys:
            result.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(result) + "\n", encoding="utf-8")


def _build_response() -> SettingsResponse:
    s = get_settings()
    return SettingsResponse(
        translation_provider=s.translation_provider,
        translation_model=s.translation_model,
        review_provider=s.review_provider,
        review_model=s.review_model,
        tagging_provider=s.tagging_provider,
        tagging_model=s.tagging_model,
        translation_review_enabled=s.translation_review_enabled,
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
    """Update application settings in-memory and persist to .env."""
    s = get_settings()
    env_updates: dict[str, str] = {}
    changed = False

    for field in (
        "translation_provider",
        "translation_model",
        "review_provider",
        "review_model",
        "tagging_provider",
        "tagging_model",
        "translation_review_enabled",
        "source_poll_url",
        "source_poll_interval_minutes",
        "auto_publish_official_news",
        "translation_review_enabled",
        "source_poll_url",
        "source_poll_interval_minutes",
        "auto_publish_official_news",
    ):
        val = getattr(body, field)
        if val is None:
            continue
        setattr(s, field, val)
        env_updates[_env_key(field)] = str(val).lower() if isinstance(val, bool) else str(val)
        changed = True

    if not changed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    _write_env_file(env_updates)
    return _build_response()
