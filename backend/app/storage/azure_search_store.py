
"""Azure AI Search document indexing and retrieval."""

import base64
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv
from langchain_core.documents import Document

from app.integrations.embedding_factory import (
    embed_documents,
    embed_query,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

VECTOR_DIMENSIONS = 3072


def get_search_client() -> SearchClient:
    """Connect to the existing Azure AI Search index."""

    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")

    if not all([endpoint, api_key, index_name]):
        raise ValueError("Azure AI Search configuration is missing.")

    return SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(api_key),
    )


def make_search_id(chunk_id: str) -> str:
    """Convert chunk IDs into Azure-compatible stable keys."""

    return base64.urlsafe_b64encode(
        chunk_id.encode("utf-8")
    ).decode("ascii").rstrip("=")


def split_element_ids(value) -> list[str]:
    """Normalize comma-separated element IDs."""

    if not value:
        return []

    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def index_chunks(chunks: list[Document]) -> int:
    """Generate embeddings and index chunks in Azure AI Search."""

    if not chunks:
        return 0

    texts = [chunk.page_content for chunk in chunks]
    vectors = embed_documents(texts)

    if len(vectors) != len(chunks):
        raise ValueError("Embedding count does not match chunk count.")

    records = []

    for chunk, vector in zip(chunks, vectors):
        if len(vector) != VECTOR_DIMENSIONS:
            raise ValueError(
                f"Invalid embedding dimension: {len(vector)}"
            )

        metadata = chunk.metadata
        chunk_id = metadata["chunk_id"]

        records.append({
            "id": make_search_id(chunk_id),
            "document_id": str(metadata["document_id"]),
            "source_file": str(metadata.get("source_file", "")),
            "page": str(metadata.get("page", "N/A")),
            "content": chunk.page_content,
            "content_type": str(metadata.get("content_type", "text")),
            "table_ids": split_element_ids(
                metadata.get("table_ids")
            ),
            "figure_ids": split_element_ids(
                metadata.get("figure_ids")
            ),
            "content_vector": vector,
        })

    client = get_search_client()
    results = client.upload_documents(documents=records)

    failed = [
        result.key
        for result in results
        if not result.succeeded
    ]

    if failed:
        raise RuntimeError(
            f"Azure AI Search indexing failed for: {failed}"
        )

    return len(results)


def search_hybrid(question: str, top_k: int = 5) -> list[dict]:
    """Run combined keyword and vector search."""

    if not question.strip():
        return []

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    vector = embed_query(question)

    if len(vector) != VECTOR_DIMENSIONS:
        raise ValueError(
            f"Expected {VECTOR_DIMENSIONS} dimensions, got {len(vector)}"
        )

    client = get_search_client()

    results = client.search(
        search_text=question,
        vector_queries=[
            VectorizedQuery(
                vector=vector,
                k_nearest_neighbors=top_k,
                fields="content_vector",
            )
        ],
        top=top_k,
        select=[
            "id",
            "document_id",
            "source_file",
            "page",
            "content",
            "content_type",
            "table_ids",
            "figure_ids",
        ],
    )

    return [
        {
            "id": result["id"],
            "document_id": result["document_id"],
            "source_file": result["source_file"],
            "page": result["page"],
            "content": result["content"],
            "content_type": result["content_type"],
            "table_ids": result.get("table_ids", []),
            "figure_ids": result.get("figure_ids", []),
            "score": result["@search.score"],
        }
        for result in results
    ]


def delete_document_from_search(document_id: str) -> int:
    """Delete all Azure AI Search chunks belonging to a document."""

    if not document_id.strip():
        raise ValueError("document_id cannot be empty.")

    client = get_search_client()

    # Escape single quotes for Azure OData filter syntax.
    safe_id = document_id.replace("'", "''")

    results = client.search(
        search_text="*",
        filter=f"document_id eq '{safe_id}'",
        select=["id"],
        top=1000,
    )

    chunk_ids = [result["id"] for result in results]

    if not chunk_ids:
        return 0

    response = client.delete_documents(
        documents=[{"id": chunk_id} for chunk_id in chunk_ids]
    )

    failed = [
        item.key
        for item in response
        if not item.succeeded
    ]

    if failed:
        raise RuntimeError(
            f"Azure AI Search deletion failed for: {failed}"
        )

    return len(chunk_ids)
