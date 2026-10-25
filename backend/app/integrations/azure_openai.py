
from langchain_openai import ChatOpenAI

from app.core.config import get_settings


def get_azure_llm() -> ChatOpenAI:
    """Create a LangChain model using the Azure OpenAI v1 API."""

    settings = get_settings()

    if not settings.azure_openai_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is missing.")

    if not settings.azure_openai_api_key:
        raise ValueError("AZURE_OPENAI_API_KEY is missing.")

    if not settings.azure_openai_chat_deployment:
        raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT is missing.")

    endpoint = settings.azure_openai_endpoint.rstrip("/")

    return ChatOpenAI(
        model=settings.azure_openai_chat_deployment,
        base_url=f"{endpoint}/openai/v1/",
        api_key=settings.azure_openai_api_key,
        temperature=0,
        max_retries=2,
        timeout=60,
    )
