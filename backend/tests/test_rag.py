
from unittest.mock import patch

from app.services.generation import NO_EVIDENCE_MESSAGE
from app.services.rag import answer_rfp_question


MOCK_EVIDENCE = [
    {
        "text": "Customer data is encrypted using AES-256.",
        "source_file": "security_policy.md",
        "page": "N/A",
        "chunk_id": "security-001",
        "distance": 0.23,
    }
]


def test_no_relevant_evidence():
    """No evidence should produce the standard fallback."""

    with patch(
        "app.services.rag.retrieve_relevant_evidence",
        return_value=[],
    ):
        result = answer_rfp_question(
            "Do you operate a satellite facility on Mars?"
        )

    assert result == {
        "answer": NO_EVIDENCE_MESSAGE,
        "sources": [],
    }


def test_valid_grounded_answer():
    """A valid citation should include supporting evidence."""

    with (
        patch(
            "app.services.rag.retrieve_relevant_evidence",
            return_value=MOCK_EVIDENCE,
        ),
        patch(
            "app.services.rag.generate_answer",
            return_value=(
                "We use AES-256 encryption. [Source 1]"
            ),
        ),
    ):
        result = answer_rfp_question(
            "How do you protect customer data?"
        )

    assert result["answer"] == (
        "We use AES-256 encryption. [Source 1]"
    )
    assert len(result["sources"]) == 1
    assert result["sources"][0]["source_id"] == "Source 1"
    assert result["sources"][0]["evidence"] == (
        "Customer data is encrypted using AES-256."
    )


def test_invalid_citation_is_rejected():
    """An unknown source reference must not be accepted."""

    with (
        patch(
            "app.services.rag.retrieve_relevant_evidence",
            return_value=MOCK_EVIDENCE,
        ),
        patch(
            "app.services.rag.generate_answer",
            return_value=(
                "We guarantee SOC 2 compliance. [Source 9]"
            ),
        ),
    ):
        result = answer_rfp_question(
            "Are you SOC 2 compliant?"
        )

    assert result == {
        "answer": NO_EVIDENCE_MESSAGE,
        "sources": [],
    }


def test_answer_without_citation_is_rejected():
    """Generated claims must contain source references."""

    with (
        patch(
            "app.services.rag.retrieve_relevant_evidence",
            return_value=MOCK_EVIDENCE,
        ),
        patch(
            "app.services.rag.generate_answer",
            return_value="We use AES-256 encryption.",
        ),
    ):
        result = answer_rfp_question(
            "How do you protect customer data?"
        )

    assert result == {
        "answer": NO_EVIDENCE_MESSAGE,
        "sources": [],
    }


def test_llm_abstention():
    """An LLM abstention should return no citations."""

    with (
        patch(
            "app.services.rag.retrieve_relevant_evidence",
            return_value=MOCK_EVIDENCE,
        ),
        patch(
            "app.services.rag.generate_answer",
            return_value=NO_EVIDENCE_MESSAGE,
        ),
    ):
        result = answer_rfp_question(
            "Do you provide a guaranteed 30-day migration?"
        )

    assert result == {
        "answer": NO_EVIDENCE_MESSAGE,
        "sources": [],
    }
