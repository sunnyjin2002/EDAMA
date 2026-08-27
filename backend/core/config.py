"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATABASE_URL = f"sqlite:///{(_PROJECT_ROOT / 'data' / 'app.db').as_posix()}"
_DEFAULT_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Runtime settings for the local MVP application."""

    app_name: str = "Elite Dangerous Translator"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = _DEFAULT_DATABASE_URL

    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    deepseek_api_key: str | None = None
    qwen_api_key: str | None = None
    anthropic_api_key: str | None = None

    translation_provider: str = "openai"
    translation_model: str = "deepseek-v4-flash"
    review_provider: str = "openai"
    review_model: str = "gpt-4o-mini"
    tagging_provider: str = "openai"
    tagging_model: str = "gpt-4o-mini"

    translation_review_enabled: bool = True
    translation_timeout_seconds: int = 300
    translation_max_retries: int = 3

    wiki_username: str | None = None
    wiki_password: str | None = None

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None

    source_poll_url: str | None = None
    source_poll_interval_minutes: int = Field(default=120, ge=1)
    auto_publish_official_news: bool = False
    news_source_type: str = "galnet_api"
    news_fallback_source_type: str = "community"
    news_polling_enabled: bool = True

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_flag(cls, value: Any) -> Any:
        """Accept common environment labels for the debug flag."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "off", "no"}:
                return False
            if normalized in {"debug", "dev", "development", "true", "1", "on", "yes"}:
                return True
        return value

    model_config = SettingsConfigDict(
        env_file=_DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    (_PROJECT_ROOT / "data").mkdir(parents=True, exist_ok=True)
    return Settings()
