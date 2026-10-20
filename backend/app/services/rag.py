
from typing import Literal

from app.services.retrieval import retrieve_relevant_evidence
from app.services.keyword_retrieval import retrieve_keyword_evidence
from app.services.hybrid_retrieval import retrieve_hybrid_evidence
from app.services.generation import (
    generate_answer,
    NO_EVIDENCE_MESSAGE,
)
from app.services.evidence_assessment import assess_evidence
from app.utils.citations import validate_citations


RetrievalMode = Literal["semantic", "bm25", "hybrid"]


def get_evidence(
    question: str,
    retrieval_mode: RetrievalMode = "semantic",
    top_k: int = 3,
) -> list[dict]:
    """Retrieve evidence using the selected retrieval strategy."""

    if retrieval_mode == "semantic":
        evidence = retrieve_relevant_evidence(
            question=question,
            top_k=top_k,
        )

    elif retrieval_mode == "bm25":
        evidence = retrieve_keyword_evidence(
            question=question,
            top_k=top_k,
        )

    elif retrieval_mode == "hybrid":
        evidence = retrieve_hybrid_evidence(
            question=question,
            top_k=top_k,
            candidate_k=10,
        )

    else:
        raise ValueError(
            f"Unsupported retrieval mode: {retrieval_mode}"
        )

    # None means cosine distance is unavailable,
    # such as for BM25-only evidence.
    return [
        {
            **item,
            "distance": item.get("distance"),
        }
        for item in evidence
    ]


def answer_rfp_question(
    question: str,
    retrieval_mode: RetrievalMode = "semantic",
) -> dict:
    """Run RAG with evidence assessment and citation validation."""

    # Step 1: Validate question
    if not question.strip():
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    # Step 2: Retrieve relevant historical evidence
    evidence = get_evidence(
        question=question,
        retrieval_mode=retrieval_mode,
        top_k=3,
    )

    if not evidence:
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    # Step 3: Assess whether the evidence supports the question
    assessment = assess_evidence(
        question=question,
        evidence=evidence,
    )

    if assessment.status == "unsupported":
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    # Step 4: Generate answer for supported or partial evidence
    answer = generate_answer(
        question=question,
        evidence=evidence,
    )

    if answer == NO_EVIDENCE_MESSAGE:
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    # Step 5: Validate source citations
    valid, sources = validate_citations(
        answer=answer,
        evidence=evidence,
    )

    if not valid:
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    # Step 6: Return the final answer and supporting sources
    return {
        "answer": answer,
        "sources": sources,
    }
