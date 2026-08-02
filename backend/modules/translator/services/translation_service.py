"""Translation service — first-pass translation with glossary + TM injection."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.db.models import Job, JobStatus, Translation
from backend.modules.translator.clients.llm_base import create_client
from backend.modules.translator.services.glossary_service import GlossaryService
from backend.modules.translator.services.job_service import JobService
from backend.modules.translator.services.translation_memory_service import TranslationMemoryService

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def _load_prompt(filename: str) -> str:
    path = PROMPT_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return _default_prompt()


def _default_prompt() -> str:
    return (
        "Translate the following Elite Dangerous article from English to Chinese.\n\n"
        "Guidelines:\n"
        "- Use the provided glossary terms where applicable.\n"
        "- Preserve lore consistency: names, factions, locations must match canon.\n"
        "- Do NOT invent facts not present in the source text.\n"
        "- Produce natural, fluent Chinese suitable for a gaming community.\n"
        "- List any terms you were unsure about at the end under [Unresolved Terms].\n"
    )


class TranslationService:
    """Coordinates first-pass translation calls."""

    def __init__(
        self,
        job_service: JobService | None = None,
        glossary_service: GlossaryService | None = None,
        tm_service: TranslationMemoryService | None = None,
    ) -> None:
        self.job_service = job_service or JobService()
        self.glossary_service = glossary_service or GlossaryService()
        self.tm_service = tm_service or TranslationMemoryService()

    async def translate_article(self, db: Session, job_id: int) -> Job:
        """Run first-pass translation on a job's article.

        1. Load the source article.
        2. Retrieve glossary matches and similar TM passages.
        3. Build the prompt and call the configured LLM provider.
        4. Save the translation and update job status.
        """
        job = self.job_service.get_job(db, job_id)
        if job is None:
            raise ValueError(f"Job {job_id} not found")
        if job.article is None:
            raise ValueError(f"Job {job_id} has no associated article")

        article = job.article
        self.job_service.add_log(db, job, "translate_start", "Beginning first-pass translation.")

        # Gather context
        source = f"Title: {article.source_title}\n\n{article.source_body}"
        glossary_entries = self.glossary_service.find_matches_for_passage(db, source)
        tm_passages = self.tm_service.retrieve_similar_passages(db, source, limit=5)

        # Build prompts
        system_prompt = _load_prompt("translate_prompt.txt")
        user_prompt = self._build_user_prompt(source, glossary_entries, tm_passages)

        if glossary_entries:
            terms = ", ".join(e.source_term_en for e in glossary_entries[:20])
            self.job_service.add_log(
                db, job, "translate_glossary",
                f"{len(glossary_entries)} glossary matches: {terms}",
            )
        if tm_passages:
            self.job_service.add_log(
                db, job, "translate_tm",
                f"{len(tm_passages)} similar TM passages retrieved",
            )

        # Call LLM
        settings = get_settings()
        provider = settings.translation_provider
        model = settings.translation_model

        provider_key_map = {
            "openai": settings.openai_api_key,
            "deepseek": settings.deepseek_api_key,
            "qwen": settings.qwen_api_key,
            "anthropic": settings.anthropic_api_key,
            "gemini": settings.gemini_api_key,
        }
        api_key = provider_key_map.get(provider)
        if not api_key:
            raise ValueError(f"No API key configured for provider '{provider}'")

        client = create_client(provider, api_key)
        response = await client.generate(
            system_prompt, user_prompt,
            model=model or "gpt-4o-mini",
            temperature=0.3,
            max_tokens=4096,
        )

        # Parse response — extract title and body
        translated_title, translated_body = self._parse_translation_response(
            response.text, article.source_title
        )

        # Save
        translation = db.query(Translation).filter_by(job_id=job_id).first()
        if translation is None:
            translation = Translation(article_id=article.id, job_id=job_id)
            db.add(translation)
        translation.translated_title = translated_title
        translation.translated_body = translated_body
        job.status = JobStatus.succeeded

        self.job_service.add_log(
            db, job, "translate_done",
            f"Translation completed via {provider}/{model}",
        )
        db.commit()
        db.refresh(job)
        return job

    # ── helpers ─────────────────────────────────────────────────

    def _build_user_prompt(
        self,
        source: str,
        glossary_entries: list,
        tm_passages: list,
    ) -> str:
        parts: list[str] = []

        if glossary_entries:
            glossary_text = "\n".join(
                f"- {e.source_term_en} → {e.approved_term_zh}"
                for e in glossary_entries[:20]
            )
            parts.append(f"Glossary (use these translations):\n{glossary_text}")

        if tm_passages:
            tm_text = "\n\n".join(
                f"Example:\nEN: {p.source_text[:300]}\nZH: {p.translated_text[:300]}"
                for p in tm_passages[:3]
            )
            parts.append(f"Reference translations (for style guidance only):\n{tm_text}")

        parts.append(f"Source text:\n{source}")
        return "\n\n".join(parts)

    @staticmethod
    def _parse_translation_response(
        text: str, fallback_title: str
    ) -> tuple[str, str]:
        """Extract translated title and body from the LLM response.

        Tries to find a title on the first line (common output pattern),
        otherwise uses the fallback title and treats the whole text as body.
        """
        lines = text.strip().split("\n")
        # If the first line looks like a standalone title (short, no period)
        if lines and len(lines[0]) < 200 and not lines[0].endswith("。"):
            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        else:
            title = fallback_title
            body = text.strip()
        return title or fallback_title, body
