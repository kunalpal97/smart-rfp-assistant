
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import get_settings
from app.integrations.azure_openai import get_azure_llm
from app.integrations.groq_client import get_llm as get_groq_llm


def get_llm() -> BaseChatModel:
    """Return the configured LLM provider."""

    settings = get_settings()
    provider = settings.llm_provider.strip().lower()

    if provider == "groq":
        return get_groq_llm()

    if provider == "azure_openai":
        return get_azure_llm()

    raise ValueError(
        f"Unsupported LLM_PROVIDER: {settings.llm_provider}. "
        "Supported values: groq, azure_openai."
    )
