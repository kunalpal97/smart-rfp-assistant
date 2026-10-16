
from app.services.retrieval import retrieve_relevant_evidence
from app.services.generation import (
    generate_answer,
    NO_EVIDENCE_MESSAGE,
)
from app.utils.citations import validate_citations


def answer_rfp_question(question: str) -> dict:
    """Run RAG with citation-reference validation."""

    if not question.strip():
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    evidence = retrieve_relevant_evidence(
        question=question,
        top_k=3,
    )

    if not evidence:
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    answer = generate_answer(question, evidence)

    if answer == NO_EVIDENCE_MESSAGE:
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    valid, sources = validate_citations(answer, evidence)

    if not valid:
        return {
            "answer": NO_EVIDENCE_MESSAGE,
            "sources": [],
        }

    return {
        "answer": answer,
        "sources": sources,
    }
