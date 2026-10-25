
from pydantic import BaseModel, Field


class KnowledgeOverview(BaseModel):
    total_documents: int = Field(ge=0)
    ready_documents: int = Field(ge=0)
    processing_documents: int = Field(ge=0)
    failed_documents: int = Field(ge=0)
    documents_needing_attention: int = Field(ge=0)
    total_chunks: int = Field(ge=0)
    latest_upload_at: str | None = None


class AnswerOverview(BaseModel):
    total_answers: int = Field(ge=0)
    answers_last_7_days: int = Field(ge=0)
    answers_with_sources: int = Field(ge=0)
    answers_without_sources: int = Field(ge=0)
    evidence_coverage_percent: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )


class DashboardOverviewResponse(BaseModel):
    knowledge: KnowledgeOverview
    answers: AnswerOverview
