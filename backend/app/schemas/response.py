
"""Pydantic schemas for AI-generated answers and cited evidence."""

from typing import Any

from pydantic import BaseModel, Field


class StructuredElementResponse(BaseModel):
    """A structured table or figure stored in PostgreSQL."""

    id: int
    document_id: str
    element_id: str
    element_type: str
    page_number: int
    content: dict[str, Any] = Field(default_factory=dict)


class SourceResponse(BaseModel):
    """One cited passage with optional structured document metadata."""

    # Existing citation fields
    source_id: str = Field(
        description="Citation label, e.g. Source 1"
    )
    source_file: str
    page: int | str | None = None
    chunk_id: str
    evidence: str

    distance: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description=(
            "Cosine distance, if available. "
            "None for Azure hybrid or BM25-only matches."
        ),
    )

    # Structured evidence metadata
    document_id: str | None = None
    content_type: str | None = None

    table_ids: list[str] = Field(default_factory=list)
    figure_ids: list[str] = Field(default_factory=list)

    structured_elements: list[StructuredElementResponse] = Field(
        default_factory=list
    )


class RFPAnswerResponse(BaseModel):
    """AI answer and the supporting cited sources."""

    answer: str
    sources: list[SourceResponse] = Field(
        default_factory=list
    )
