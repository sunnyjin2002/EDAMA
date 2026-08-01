"""OpenAI client — uses the `openai` SDK for chat completions."""

from __future__ import annotations

from openai import AsyncOpenAI

from backend.modules.translator.clients.llm_base import LLMClient, LLMResponse


class OpenAIClient(LLMClient):
    """OpenAI chat-completion client."""

    provider_name = "openai"

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        model: str | None = None,
    ) -> LLMResponse:
        effective_model = model or "gpt-4o-mini"
        completion = await self._client.chat.completions.create(
            model=effective_model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return LLMResponse(
            text=completion.choices[0].message.content or "",
            model=effective_model,
            provider=self.provider_name,
        )
