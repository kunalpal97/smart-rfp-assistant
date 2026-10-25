
from functools import lru_cache

from openai import OpenAI

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_azure_embedding_client() -> OpenAI:
    """Create a reusable Azure OpenAI client."""

    settings = get_settings()

    if not settings.azure_openai_endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT is missing.")

    if not settings.azure_openai_api_key:
        raise ValueError("AZURE_OPENAI_API_KEY is missing.")

    if not settings.azure_openai_embedding_deployment:
        raise ValueError(
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT is missing."
        )

    endpoint = settings.azure_openai_endpoint.rstrip("/")

    return OpenAI(
        base_url=f"{endpoint}/openai/v1/",
        api_key=settings.azure_openai_api_key,
        timeout=60.0,
        max_retries=2,
    )


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Generate Azure embeddings for document chunks."""

    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError("Cannot embed empty document text.")

    settings = get_settings()
    client = get_azure_embedding_client()

    response = client.embeddings.create(
        model=settings.azure_openai_embedding_deployment,
        input=texts,
    )

    # Preserve original input order.
    ordered = sorted(response.data, key=lambda item: item.index)

    return [item.embedding for item in ordered]


def embed_query(text: str) -> list[float]:
    """Generate Azure embedding for a user question."""

    if not text.strip():
        raise ValueError("Cannot embed an empty question.")

    return embed_documents([text])[0]
