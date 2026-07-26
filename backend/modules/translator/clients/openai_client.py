"""OpenAI client placeholder."""

from backend.modules.translator.clients.llm_base import LLMClient


class OpenAIClient:
    """OpenAI client shell for a future phase."""

    provider_name = "openai"


def get_client() -> LLMClient:
    """Return the OpenAI client placeholder."""
    return OpenAIClient()
