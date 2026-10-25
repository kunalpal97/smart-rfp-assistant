
from pathlib import Path

import chromadb  # type: ignore
from langchain_core.documents import Document
from app.core.config import get_settings

from app.integrations.embedding_factory import (
    embed_documents,
    embed_query,
)


LOCAL_COLLECTION_NAME = "historical_proposals"
AZURE_COLLECTION_NAME = "historical_proposals_azure"



def get_collection():
    """Open the collection matching the embedding provider."""

    settings = get_settings()

    provider = settings.embedding_provider.strip().lower()

    if provider == "azure_openai":
        collection_name = AZURE_COLLECTION_NAME

    elif provider == "local":
        collection_name = LOCAL_COLLECTION_NAME

    else:
        raise ValueError(
            f"Unsupported embedding provider: {provider}"
        )

    chroma_path = settings.chroma_dir
    chroma_path.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(
        path=str(chroma_path)
    )

    return client.get_or_create_collection(
        name=collection_name,
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



def delete_document_from_all_collections(
    document_id: str,
) -> int:
    """Delete a document's records from all known Chroma collections."""

    settings = get_settings()

    client = chromadb.PersistentClient(
        path=str(settings.chroma_dir)
    )

    collection_names = [
        "historical_proposals",
        "historical_proposals_azure",
    ]

    total_deleted = 0

    for collection_name in collection_names:
        try:
            collection = client.get_collection(
                name=collection_name
            )
        except chromadb.errors.NotFoundError:
            continue

        results = collection.get(
            where={"document_id": document_id}
        )

        chunk_ids = results["ids"]

        if not chunk_ids:
            continue

        collection.delete(ids=chunk_ids)

        # Verify that the records were removed.
        remaining = collection.get(
            where={"document_id": document_id}
        )

        if remaining["ids"]:
            raise RuntimeError(
                f"Deletion verification failed in {collection_name}"
            )

        total_deleted += len(chunk_ids)

    return total_deleted

