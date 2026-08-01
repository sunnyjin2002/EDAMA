"""DeepSeek client — uses the `openai` SDK against the DeepSeek API endpoint."""

from __future__ import annotations

from backend.modules.translator.clients.openai_client import OpenAIClient

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


class DeepSeekClient(OpenAIClient):
    """DeepSeek chat-completion client — OpenAI-compatible API."""

    provider_name = "deepseek"

    def __init__(self, api_key: str) -> None:
        super().__init__(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
