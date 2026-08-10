"""Tagging service — hybrid glossary/entity matching + LLM tag extraction."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.db.models import ArticleTag, Job, JobLog, Tag, TagType
from backend.modules.translator.clients.llm_base import create_client
from backend.modules.translator.services.glossary_service import GlossaryService
from backend.modules.translator.services.job_service import JobService


class TaggingService:
    """Extracts and stores tags for articles."""

    def __init__(
        self,
        job_service: JobService | None = None,
        glossary_service: GlossaryService | None = None,
    ) -> None:
        self.job_service = job_service or JobService()
        self.glossary_service = glossary_service or GlossaryService()

    async def extract_tags(self, db: Session, job_id: int) -> Job | None:
        """Run tag extraction on a job's article.

        Uses a hybrid approach: glossary/entity matching first, then
        LLM for additional tags.  Tags are merged and deduplicated.
        """
        job = self.job_service.get_job(db, job_id)
        if job is None or job.article is None:
            return None

        article = job.article
        self.job_service.add_log(db, job, "tag_start", "Beginning tag extraction.")

        source = f"{article.source_title}\n\n{article.source_body}"

        # 1. Extract tags from glossary / entity matching
        glossary_matches = self.glossary_service.find_matches_for_passage(db, source)
        glossary_tags: set[str] = set()
        for entry in glossary_matches:
            if entry.entity_type:
                for t in (s.strip() for s in entry.entity_type.split(",")):
                    glossary_tags.add(t.lower().replace(" ", "-"))

        # 2. LLM-generated tags
        settings = get_settings()
        provider = settings.tagging_provider
        model = settings.tagging_model
        provider_key_map = {
            "openai": settings.openai_api_key,
            "deepseek": settings.deepseek_api_key,
            "qwen": settings.qwen_api_key,
            "anthropic": settings.anthropic_api_key,
            "gemini": settings.gemini_api_key,
        }
        api_key = provider_key_map.get(provider)

        llm_tags: set[str] = set()
        if api_key:
            try:
                client = create_client(provider, api_key)
                response = await client.generate(
                    "You are a content tagger. Return only lowercase tags, one per line.",
                    f"Article:\n{source[:2000]}",
                    model=model or "gpt-4o-mini",
                    temperature=0.2,
                    max_tokens=256,
                )
                for line in response.text.splitlines():
                    tag = line.strip().lower()
                    if tag and len(tag) < 50 and not tag.startswith("#"):
                        llm_tags.add(tag)
            except Exception:
                self.job_service.add_log(
                    db, job, "tag_llm_failed",
                    "LLM tag extraction failed, falling back to glossary tags only",
                )

        # 3. Merge and deduplicate
        all_tags = glossary_tags | llm_tags
        if not all_tags:
            self.job_service.add_log(db, job, "tag_done", "No tags extracted.")
            db.commit()
            return job

        # Store
        saved = 0
        for tag_name in all_tags:
            tag = db.scalar(select(Tag).where(Tag.name == tag_name))
            if tag is None:
                # Determine tag type
                tag_type = TagType.topic
                if tag_name in glossary_tags and tag_name not in llm_tags:
                    tag_type = TagType.entity
                tag = Tag(name=tag_name, tag_type=tag_type)
                db.add(tag)
                db.flush()
            # Link to article if not already linked
            link = db.scalar(
                select(ArticleTag).where(
                    ArticleTag.article_id == article.id,
                    ArticleTag.tag_id == tag.id,
                )
            )
            if link is None:
                db.add(ArticleTag(article_id=article.id, tag_id=tag.id))
                saved += 1

        self.job_service.add_log(
            db, job, "tag_done",
            f"Extracted {saved} tags: {', '.join(sorted(all_tags))}",
        )
        db.commit()
        return job
