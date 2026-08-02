"""Anthropic client stub — requires `anthropic` package for full implementation."""

from __future__ import annotations

from backend.modules.translator.clients.llm_base import LLMClient, LLMResponse


class AnthropicClient(LLMClient):
    """Anthropic Claude client — currently a stub.
    Install ``anthropic`` and implement :meth:`generate` with the
    Anthropic Messages API when needed."""

    provider_name = "anthropic"

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
            "Anthropic client is not yet implemented. "
            "Install `anthropic` and wire up the Messages API."
        )
