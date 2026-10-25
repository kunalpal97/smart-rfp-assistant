

# This code is when you have to use the local embedding like MiniLM 

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the configured local embedding model once."""

    settings = get_settings()

    return SentenceTransformer(
        settings.local_embedding_model,
        device="cpu",
    )


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Convert document chunks into vectors."""

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return vectors.tolist()


def embed_query(text: str) -> list[float]:
    """Convert a user question into a vector."""

    return embed_documents([text])[0]
