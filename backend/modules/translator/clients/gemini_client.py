"""Gemini client stub — requires `google-generativeai` to be installed."""

from __future__ import annotations

from backend.modules.translator.clients.llm_base import LLMClient, LLMResponse


class GeminiClient(LLMClient):
    """Gemini client — currently a stub.  Install ``google-generativeai``
    and implement :meth:`generate` with the Gemini API when needed."""

    provider_name = "gemini"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        model: str | None = None,
    ) -> LLMResponse:
        raise NotImplementedError(
            "Gemini client is not yet implemented. "
            "Install `google-generativeai` and wire up the API."
        )
