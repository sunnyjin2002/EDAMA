"""Review service — LLM-powered translation review with deterministic checks."""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy.orm import Session

from backend.core.config import get_settings
from backend.db.models import Job, JobStatus, Translation
from backend.modules.translator.clients.llm_base import create_client
from backend.modules.translator.services.glossary_service import GlossaryService
from backend.modules.translator.services.job_service import JobService

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"

# Characters that indicate Chinese text — used for English-fragment detection
_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
# English word pattern
_WORD_RE = re.compile(r"\b[a-zA-Z]{3,}\b")


def _load_prompt(filename: str) -> str:
    path = PROMPT_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "Review the translation for accuracy and quality."


class ReviewService:
    """Coordinates translation review — deterministic checks + LLM."""

    def __init__(
        self,
        job_service: JobService | None = None,
        glossary_service: GlossaryService | None = None,
    ) -> None:
        self.job_service = job_service or JobService()
        self.glossary_service = glossary_service or GlossaryService()

    async def review_translation(self, db: Session, job_id: int) -> Job | None:
        """Run review on a job's translation.

        Returns the job if review completed, or ``None`` if review was
        skipped (e.g. the toggle is off or no translation exists).
        """
        settings = get_settings()
        if not settings.translation_review_enabled:
            return None

        job = self.job_service.get_job(db, job_id)
        if job is None or job.article is None:
            return None

        # Find the first-pass translation
        translation = db.query(Translation).filter_by(job_id=job_id).first()
        if translation is None or not translation.translated_body:
            # Force expire and reload — the translation may have been
            # committed in a different session
            db.expire_all()
            translation = db.query(Translation).filter_by(job_id=job_id).first()
        if translation is None or not translation.translated_body:
            return None

        self.job_service.add_log(db, job, "review_start", "Beginning translation review.")
        db.commit()

        source = f"Title: {job.article.source_title}\n\n{job.article.source_body}"
        first_pass = f"Title: {translation.translated_title or ''}\n\n{translation.translated_body or ''}"

        # Deterministic checks
        checks = self._run_deterministic_checks(source, first_pass, db)

        # LLM review
        glossary_entries = self.glossary_service.find_matches_for_passage(db, source)
        system_prompt = _load_prompt("review_prompt.txt")
        user_prompt = self._build_review_prompt(source, first_pass, checks, glossary_entries)

        provider = settings.review_provider
        model = settings.review_model
        provider_key_map = {
            "openai": settings.openai_api_key,
            "deepseek": settings.deepseek_api_key,
            "qwen": settings.qwen_api_key,
            "anthropic": settings.anthropic_api_key,
            "gemini": settings.gemini_api_key,
        }
        api_key = provider_key_map.get(provider)
        if not api_key:
            raise ValueError(f"No API key configured for review provider '{provider}'")

        client = create_client(provider, api_key)
        response = await client.generate(
            system_prompt,
            user_prompt,
            model=model or "gpt-4o-mini",
            temperature=0.2,
            max_tokens=4096,
        )

        # Parse structured output
        reviewed_title, reviewed_body, notes, score = self._parse_review_response(
            response.text,
            translation.translated_title or "",
            translation.translated_body or "",
        )

        # Save
        translation.reviewed_title = reviewed_title
        translation.reviewed_body = reviewed_body
        translation.review_notes = notes
        translation.confidence_score = score

        self.job_service.add_log(
            db, job, "review_done",
            f"Review completed via {provider}/{model}. "
            f"Checks: {checks['summary']}. Score: {score:.2f}",
        )
        db.commit()
        db.refresh(job)
        return job

    # ── deterministic checks ────────────────────────────────────

    @staticmethod
    def _run_deterministic_checks(
        source: str,
        translated: str,
        db: Session | None,
    ) -> dict[str, object]:
        """Run heuristics: English fragments, structural mismatch."""
        issues: list[str] = []

        # 1. Leftover English fragments
        eng_words = _WORD_RE.findall(translated)
        if eng_words:
            # Filter out proper nouns that should stay in English
            common_keep = {"HIP", "LY", "LS", "Mm", "AU"}
            fragments = [w for w in eng_words if w not in common_keep]
            if fragments:
                issues.append(f"Possible English fragments: {', '.join(fragments[:10])}")

        # 2. Structural check — paragraph count
        src_paras = [p for p in source.split("\n\n") if p.strip()]
        tgt_paras = [p for p in translated.split("\n\n") if p.strip()]
        if len(src_paras) > 1 and abs(len(src_paras) - len(tgt_paras)) > len(src_paras) * 0.5:
            issues.append(
                f"Paragraph count mismatch: source={len(src_paras)}, translation={len(tgt_paras)}"
            )

        # 3. CJK ratio check
        cjk_chars = len(_CJK_RE.findall(translated))
        total_chars = len(translated.replace(" ", "").replace("\n", ""))
        if total_chars > 20 and cjk_chars / max(total_chars, 1) < 0.15:
            issues.append("Very low CJK character ratio — may not be Chinese")

        return {
            "issues": issues,
            "summary": f"{len(issues)} issue(s)" if issues else "no issues",
        }

    # ── helpers ─────────────────────────────────────────────────

    @staticmethod
    def _build_review_prompt(
        source: str,
        first_pass: str,
        checks: dict[str, object],
        glossary_entries: list,
    ) -> str:
        parts: list[str] = []

        parts.append(f"ORIGINAL (English):\n{source}")
        parts.append(f"FIRST-PASS TRANSLATION:\n{first_pass}")

        if glossary_entries:
            glossary_text = "\n".join(
                f"- {e.source_term_en} → {e.approved_term_zh}"
                for e in glossary_entries[:20]
            )
            parts.append(f"GLOSSARY (must use these terms):\n{glossary_text}")

        issues = checks.get("issues", [])
        if issues:
            parts.append(
                "AUTOMATED CHECKS found potential problems:\n"
                + "\n".join(f"- {i}" for i in issues)
            )

        return "\n\n".join(parts)

    @staticmethod
    def _parse_review_response(
            text: str,
            fallback_title: str,
            fallback_body: str,
    ) -> tuple[str, str, str, float]:
        """Parse review output with TITLE/BODY/NOTES/SCORE sections."""
        title = fallback_title
        body = fallback_body
        notes = ""
        score = 0.8

        # Extract sections by finding section headers
        sections: dict[str, str] = {}
        current_key: str | None = None
        current_lines: list[str] = []
        headers = {"TITLE", "BODY", "NOTES", "SCORE"}

        for line in text.splitlines():
            stripped = line.strip()
            upper = stripped.upper()
            # Check if this line starts a new section
            matched = False
            for h in headers:
                if upper.startswith(f"{h}:") or upper.startswith(f"{h}："):
                    # Save previous section
                    if current_key:
                        sections[current_key] = "\n".join(current_lines).strip()
                    current_key = h
                    # Value is after the colon
                    sep = ":" if f"{h}:" in upper else "："
                    val = stripped.split(sep, 1)[-1].strip()
                    current_lines = [val] if val else []
                    matched = True
                    break
            if not matched and current_key:
                current_lines.append(stripped)

        # Save last section
        if current_key and current_lines:
            sections[current_key] = "\n".join(current_lines).strip()

        if sections.get("TITLE"):
            title = sections["TITLE"]
        if sections.get("BODY"):
            body = sections["BODY"]
        if sections.get("NOTES"):
            notes = sections["NOTES"]
        if sections.get("SCORE"):
            try:
                s = float(sections["SCORE"].split()[0])
                score = max(0.0, min(1.0, s))
            except (ValueError, IndexError):
                pass

        return title or fallback_title, body or fallback_body, notes, score
