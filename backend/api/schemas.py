"""Pydantic response schemas for the EDAMA REST API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Article schemas ────────────────────────────────────────────────

class ArticleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str | None
    article_header: str | None
    source_type: str
    source_url: str | None
    source_title: str
    published_at_source: datetime | None
    discovered_at: datetime | None
    created_at: datetime


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    job_type: str
    status: str
    target_language: str
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    article: ArticleSummary | None = None


class JobLogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stage: str
    message: str
    created_at: datetime


class JobDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    job_type: str
    status: str
    target_language: str
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    article: ArticleSummary | None = None
    logs: list[JobLogEntry] = []
    translated_title: str | None = None
    translated_body: str | None = None
    reviewed_title: str | None = None
    reviewed_body: str | None = None
    review_notes: str | None = None
    confidence_score: float | None = None
    tags: list[str] = []


class ArticleTranslationDetail(BaseModel):
    language: str
    translated_title: str | None
    translated_body: str | None
    reviewed_title: str | None
    reviewed_body: str | None
    review_notes: str | None
    confidence_score: float | None


class ArticleDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str | None
    article_header: str | None
    source_type: str
    source_url: str | None
    source_title: str
    source_body: str
    published_at_source: datetime | None
    discovered_at: datetime | None
    created_at: datetime
    updated_at: datetime | None
    jobs: list[JobDetail] = []
    translations: list[ArticleTranslationDetail] = Field(
        default_factory=list,
        validation_alias="article_translations",
    )


class ArticleArchiveItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str | None
    article_header: str | None
    source_type: str
    source_url: str | None
    source_title: str
    published_at_source: datetime | None
    discovered_at: datetime | None


class ArticleListResponse(BaseModel):
    articles: list[ArticleArchiveItem]
    type: str = ""

# ── Dashboard ──────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    app_name: str
    recent_jobs: list[JobSummary]


# ── Manual submission ──────────────────────────────────────────────

class ManualSubmissionRequest(BaseModel):
    title: str | None = None
    source_url: str | None = None
    source_text: str
    target_language: str = "zh-CN"


class ManualSubmissionResponse(BaseModel):
    article: ArticleSummary
    job: JobSummary
    message: str


class ManualSubmissionError(BaseModel):
    errors: list[str]


# ── Glossary ───────────────────────────────────────────────────────

class GlossaryEntryDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_term_en: str
    approved_term_zh: str
    aliases_en: str | None
    entity_type: str | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class GlossaryListResponse(BaseModel):
    entries: list[GlossaryEntryDetail]
    query: str = ""


class GlossaryImportResponse(BaseModel):
    message: str
    file_name: str
    inserted: int
    updated: int
    skipped: int
    errors: list[str]


class GlossaryCreateRequest(BaseModel):
    source_term_en: str
    approved_term_zh: str
    aliases_en: str | None = None
    entity_type: str | None = None
    notes: str | None = None
    status: str = "draft"


# ── Translation memory ─────────────────────────────────────────────

class TranslationMemoryEntryDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_text: str
    translated_text: str
    source_reference: str | None
    tags: str | None
    created_at: datetime


class TranslationMemoryListResponse(BaseModel):
    entries: list[TranslationMemoryEntryDetail]
    matches: list[TranslationMemoryEntryDetail] = []
    query: str = ""


class TranslationMemoryImportResponse(BaseModel):
    message: str
    file_name: str
    inserted: int
    updated: int
    skipped: int
    errors: list[str]


# ── Health ──────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str


# ── Settings ────────────────────────────────────────────────────────

class SettingsResponse(BaseModel):
    translation_provider: str
    translation_model: str
    review_provider: str
    review_model: str
    tagging_provider: str
    tagging_model: str
    translation_review_enabled: bool
    news_source_type: str
    news_polling_enabled: bool
    source_poll_url: str | None
    source_poll_interval_minutes: int
    auto_publish_official_news: bool


class SettingsUpdateRequest(BaseModel):
    translation_provider: str | None = None
    translation_model: str | None = None
    review_provider: str | None = None
    review_model: str | None = None
    tagging_provider: str | None = None
    tagging_model: str | None = None
    translation_review_enabled: bool | None = None
    news_source_type: str | None = None
    news_polling_enabled: bool | None = None
    source_poll_url: str | None = None
    source_poll_interval_minutes: int | None = None
    auto_publish_official_news: bool | None = None


class ArticlePollResponse(BaseModel):
    """Summary returned after a manual news polling cycle."""

    fetched: int
    created: int
    skipped: int
    failed: int
    errors: list[str]
