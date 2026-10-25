

"""Pydantic response schemas for answer history."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HistoryEntry(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    question: str
    answer: str
    sources: list[dict[str, Any]]
    created_at: datetime



class HistoryListResponse(BaseModel):
    items: list[HistoryEntry]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)



class HistoryDeleteResponse(BaseModel):
    message: str
