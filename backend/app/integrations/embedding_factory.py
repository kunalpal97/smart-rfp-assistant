
from app.core.config import get_settings

from app.integrations.azure_embeddings import (
    embed_documents as azure_embed_documents,
    embed_query as azure_embed_query,
)

from app.integrations.local_embeddings import (
    embed_documents as local_embed_documents,
    embed_query as local_embed_query,
)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Generate document embeddings using configured provider."""

    provider = get_settings().embedding_provider.strip().lower()

    if provider == "azure_openai":
        return azure_embed_documents(texts)

    if provider == "local":
        return local_embed_documents(texts)

    raise ValueError(
        f"Unsupported embedding provider: {provider}"
    )


def embed_query(text: str) -> list[float]:
    """Generate query embedding using configured provider."""

    provider = get_settings().embedding_provider.strip().lower()

    if provider == "azure_openai":
        return azure_embed_query(text)

    if provider == "local":
        return local_embed_query(text)

    raise ValueError(
        f"Unsupported embedding provider: {provider}"
    )
