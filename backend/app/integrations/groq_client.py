
from langchain_groq import ChatGroq

from app.core.config import get_settings


def get_llm() -> ChatGroq:
    """Create a Groq chat model using central configuration."""

    settings = get_settings()

    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from application configuration."
        )

    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0,
        max_retries=2,
    )
