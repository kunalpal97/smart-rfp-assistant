
from pathlib import Path

import chromadb # type: ignore
from langchain_core.documents import Document

from app.integrations.local_embeddings import (
    embed_documents,
    embed_query,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHROMA_PATH = PROJECT_ROOT / "storage" / "chroma"

COLLECTION_NAME = "historical_proposals"


def get_collection():
    """Open or create our persistent ChromaDB collection."""

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def store_chunks(chunks: list[Document]) -> int:
    """Embed and store document chunks."""

    if not chunks:
        return 0

    texts = [chunk.page_content for chunk in chunks]
    embeddings = embed_documents(texts)

    collection = get_collection()

    collection.upsert(
        ids=[chunk.metadata["chunk_id"] for chunk in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[chunk.metadata for chunk in chunks],
    )

    return len(chunks)


from app.integrations.local_embeddings import (
    embed_documents,
    embed_query,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHROMA_PATH = PROJECT_ROOT / "storage" / "chroma"

COLLECTION_NAME = "historical_proposals"


def get_collection():
    """Open or create our persistent ChromaDB collection."""

    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def store_chunks(chunks: list[Document]) -> int:
    """Embed and store document chunks."""

    if not chunks:
        return 0

    texts = [chunk.page_content for chunk in chunks]
    embeddings = embed_documents(texts)

    collection = get_collection()

    collection.upsert(
        ids=[chunk.metadata["chunk_id"] for chunk in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[chunk.metadata for chunk in chunks],
    )

    return len(chunks)


def search_chunks(question: str, top_k: int = 3):
    """Retrieve document chunks similar to a question."""

    collection = get_collection()

    if collection.count() == 0:
        return []

    question_vector = embed_query(question)

    return collection.query(
        query_embeddings=[question_vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

