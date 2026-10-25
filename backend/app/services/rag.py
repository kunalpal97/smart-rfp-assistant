
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
from app.core.config import get_settings
from app.services.azure_search_retrieval import retrieve_azure_evidence
from app.storage.structured_content_repository import (
    get_document_elements,
)


RetrievalMode = Literal["semantic", "bm25", "hybrid"]



def get_evidence(
    question: str,
    retrieval_mode: RetrievalMode = "semantic",
    top_k: int = 3,
) -> list[dict]:
    """Retrieve evidence from the configured provider."""

    if not question.strip() or top_k <= 0:
        return []

    settings = get_settings()
    provider = settings.vector_store_provider.lower()

    if provider == "azure_search":
        # Azure AI Search currently uses hybrid retrieval
        # regardless of the legacy retrieval mode.
        evidence = retrieve_azure_evidence(
            question=question,
            top_k=top_k,
        )

    elif provider == "chroma":
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

    else:
        raise ValueError(
            f"Unsupported vector store provider: {provider}"
        )

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

    
    # Step 6: Attach structured tables and figures
    # only when the retrieved chunk references them.

    elements_cache: dict[str, list[dict]] = {}

    for source in sources:
        source["structured_elements"] = []

        document_id = source.get("document_id")

        if not document_id:
            continue

        table_ids = set(source.get("table_ids") or [])
        figure_ids = set(source.get("figure_ids") or [])

        if not table_ids and not figure_ids:
            continue

        if document_id not in elements_cache:
            elements_cache[document_id] = get_document_elements(
                document_id
            )

        matched_elements = []

        for element in elements_cache[document_id]:
            if (
                element["element_type"] == "table"
                and element["element_id"] in table_ids
            ):
                matched_elements.append(element)

            elif (
                element["element_type"] == "figure"
                and element["element_id"] in figure_ids
            ):
                matched_elements.append(element)

        source["structured_elements"] = matched_elements

    return {
        "answer": answer,
        "sources": sources,
    }

