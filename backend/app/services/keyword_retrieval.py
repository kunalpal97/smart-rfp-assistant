

import re

from rank_bm25 import BM25Okapi

from app.storage.vector_store import get_collection


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase searchable tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def retrieve_keyword_evidence(
    question: str,
    top_k: int = 5,
) -> list[dict]:
    """Retrieve document chunks using BM25 keyword ranking."""

    if not question.strip() or top_k <= 0:
        return []

    collection = get_collection()

    results = collection.get(
        include=["documents", "metadatas"]
    )

    chunk_ids = results["ids"]
    documents = results["documents"]
    metadatas = results["metadatas"]

    if not chunk_ids:
        return []

    tokenized_documents = [
        tokenize(text) for text in documents
    ]

    bm25 = BM25Okapi(tokenized_documents)

    query_tokens = tokenize(question)

    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True,
    )

    evidence = []

    for index in ranked_indices:
        score = float(scores[index])

        if score <= 0:
            continue

        metadata = metadatas[index]

        evidence.append({
            "text": documents[index],
            "source_file": metadata.get("source_file"),
            "page": metadata.get("page"),
            "chunk_id": chunk_ids[index],
            "bm25_score": round(score, 4),
        })

        if len(evidence) >= top_k:
            break

    return evidence
