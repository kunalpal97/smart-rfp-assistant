
from app.storage.vector_store import search_chunks


def retrieve_evidence(question: str, top_k: int = 3) -> list[dict]:
    """Retrieve relevant document passages with source metadata."""

    if not question.strip():
        return []

    results = search_chunks(question, top_k=top_k)

    if not results:
        return []

    evidence = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for text, metadata, distance in zip(
        documents, metadatas, distances
    ):
        evidence.append({
            "text": text,
            "source_file": metadata.get("source_file"),
            "page": metadata.get("page"),
            "chunk_id": metadata.get("chunk_id"),
            "distance": round(float(distance), 4),
        })

    return evidence




NO_EVIDENCE_MESSAGE = (
    "No relevant information found in historical proposals."
)

# Experimental threshold; we will tune this with evaluation data.
MAX_COSINE_DISTANCE = 0.65


def filter_evidence(
    evidence: list[dict],
    max_distance: float = MAX_COSINE_DISTANCE,
) -> list[dict]:
    """Keep only evidence within the allowed cosine distance."""

    return [
        item
        for item in evidence
        if item["distance"] <= max_distance
    ]


def retrieve_relevant_evidence(
    question: str,
    top_k: int = 3,
) -> list[dict]:
    """Retrieve and filter potentially relevant evidence."""

    evidence = retrieve_evidence(question, top_k=top_k)

    return filter_evidence(evidence)
