"""Qwen client — uses the `openai` SDK against the Alibaba Qwen API endpoint."""

from __future__ import annotations

from backend.modules.translator.clients.openai_client import OpenAIClient

QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class QwenClient(OpenAIClient):
    """Qwen chat-completion client — OpenAI-compatible API."""

    provider_name = "qwen"

    def __init__(self, api_key: str) -> None:
        super().__init__(api_key=api_key, base_url=QWEN_BASE_URL)
