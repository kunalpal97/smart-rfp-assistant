
from functools import lru_cache

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the model once and reuse it."""
    return SentenceTransformer(MODEL_NAME, device="cpu")


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
