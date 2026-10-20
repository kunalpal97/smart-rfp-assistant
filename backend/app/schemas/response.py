
from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    """One cited historical document passage."""

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
    description="Cosine distance, if available. None for BM25-only matches.",
)


class RFPAnswerResponse(BaseModel):
    """Structured response for an RFP question."""

    answer: str
    sources: list[SourceResponse] = Field(
        default_factory=list
    )
