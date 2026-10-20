

from app.services.retrieval import retrieve_evidence
from app.services.keyword_retrieval import retrieve_keyword_evidence


def retrieve_hybrid_evidence(
    question: str,
    top_k: int = 5,
    candidate_k: int = 10,
    rrf_k: int = 60,
) -> list[dict]:
    """Combine semantic and BM25 rankings using RRF."""

    if not question.strip() or top_k <= 0:
        return []

    semantic_results = retrieve_evidence(
        question,
        top_k=candidate_k,
    )

    keyword_results = retrieve_keyword_evidence(
        question,
        top_k=candidate_k,
    )

    combined = {}

    for method, results in [
        ("semantic", semantic_results),
        ("keyword", keyword_results),
    ]:
        for rank, item in enumerate(results, start=1):
            chunk_id = item["chunk_id"]

            if chunk_id not in combined:
                combined[chunk_id] = {
                    "text": item["text"],
                    "source_file": item["source_file"],
                    "page": item["page"],
                    "chunk_id": chunk_id,
                    "distance": None,
                    "bm25_score": None,
                    "rrf_score": 0.0,
                    "matched_by": [],
                }

            record = combined[chunk_id]

            weight = 1.0 if method == "semantic" else 1.5

            record["rrf_score"] += weight / (rrf_k + rank)
            record["matched_by"].append(method)

            if method == "semantic":
                record["distance"] = item["distance"]

            if method == "keyword":
                record["bm25_score"] = item["bm25_score"]

    ranked = sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )

    return ranked[:top_k]
