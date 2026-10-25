
import base64

from app.storage.azure_search_store import search_hybrid


def decode_search_id(encoded_id: str) -> str:
    """Recover the original chunk ID from Azure Search's encoded key."""
    padding = "=" * (-len(encoded_id) % 4)

    return base64.urlsafe_b64decode(
        encoded_id + padding
    ).decode("utf-8")


def retrieve_azure_evidence(
    question: str,
    top_k: int = 3,
) -> list[dict]:
    """Convert Azure AI Search results into RAG evidence."""

    if not question.strip() or top_k <= 0:
        return []

    results = search_hybrid(
        question=question,
        top_k=top_k,
    )

    evidence = []

    for result in results:
        evidence.append({
            "text": result["content"],
            "document_id": result.get("document_id"),
            "source_file": result.get("source_file"),
            "page": result.get("page"),
            "chunk_id": decode_search_id(result["id"]),
            "distance": None,
            "search_score": result.get("score"),
            "content_type": result.get("content_type"),
            "table_ids": result.get("table_ids") or [],
            "figure_ids": result.get("figure_ids") or [],
            "document_id": result.get("document_id"),
        })

    return evidence
