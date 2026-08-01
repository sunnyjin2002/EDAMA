"""Base abstractions for LLM clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """Normalised response from any LLM provider."""

    text: str
    model: str
    provider: str


class LLMClient(ABC):
    """Abstract base for LLM provider clients.

    Every provider implements :meth:`generate` which accepts a system
    prompt, a user prompt, and optional generation parameters.  The
    response is normalised into :class:`LLMResponse`.
    """

    provider_name: str

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        model: str | None = None,
    ) -> LLMResponse:
        """Send prompts to the provider and return a normalised response."""
        ...


def create_client(provider: str, api_key: str | None) -> LLMClient:
    """Factory that returns the correct LLM client for *provider*.

    Supported providers:
    - ``openai``
    - ``deepseek``
    - ``gemini`` (stub — raises NotImplementedError)
    """
    if provider == "openai":
        from backend.modules.translator.clients.openai_client import OpenAIClient

        return OpenAIClient(api_key=api_key or "")

    if provider == "deepseek":
        from backend.modules.translator.clients.deepseek_client import DeepSeekClient

        return DeepSeekClient(api_key=api_key or "")

    if provider == "gemini":
        from backend.modules.translator.clients.gemini_client import GeminiClient

        return GeminiClient(api_key=api_key or "")

    raise ValueError(f"Unknown LLM provider: {provider}")
