
from pathlib import Path

import chromadb  # type: ignore
from langchain_core.documents import Document
from app.core.config import get_settings

from app.integrations.local_embeddings import (
    embed_documents,
    embed_query,
)



COLLECTION_NAME = "historical_proposals"


def get_collection():
    """Open or create our persistent ChromaDB collection."""

    chroma_path = get_settings().chroma_dir

    # Ensure the database directory exists.
    chroma_path.mkdir(parents=True, exist_ok=True)

    # Initialize the persistent ChromaDB client.
    client = chromadb.PersistentClient(
        path=str(chroma_path)
    )

    # Return the existing collection or create it.
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )



def store_chunks(chunks: list[Document]) -> int:
    """Embed and store document chunks in ChromaDB."""

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
    """Retrieve the most relevant document chunks."""

    if not question.strip():
        return []

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    collection = get_collection()
    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    question_vector = embed_query(question)

    return collection.query(
        query_embeddings=[question_vector],
        n_results=min(top_k, total_chunks),
        include=["documents", "metadatas", "distances"],
    )



def find_document_by_hash(file_hash: str) -> dict | None:
    """Find an indexed document with identical file content."""

    collection = get_collection()

    results = collection.get(
        where={"file_hash": file_hash},
        include=["metadatas"],
        limit=1,
    )

    if not results["ids"]:
        return None

    return results["metadatas"][0]


def get_document_chunks(document_id: str) -> dict:
    """Find all indexed chunks belonging to one document."""

    collection = get_collection()

    return collection.get(
        where={"document_id": document_id},
        include=["metadatas"],
    )


def delete_document_chunks(chunk_ids: list[str]) -> None:
    """Delete specific indexed chunks."""

    if chunk_ids:
        get_collection().delete(ids=chunk_ids)
