"""SQLAlchemy ORM models for application data."""

from sqlalchemy import (
    CheckConstraint,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy import ForeignKey, JSON, UniqueConstraint


class Base(DeclarativeBase):
    """Base class for database models."""
    pass


class Document(Base):
    """Admin-managed shared document registry."""

    __tablename__ = "documents"

    document_id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
    )

    filename: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    file_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    updated_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    storage_provider: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="local",
        server_default="local",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('processing', 'ready', 'failed')",
            name="ck_documents_status",
        ),
    )


class AnswerHistory(Base):
    """User-specific RAG question and answer history."""

    __tablename__ = "answer_history"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
    )

    tenant_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    user_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    sources_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
        server_default="[]",
    )

    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    __table_args__ = (
    Index(
        "idx_history_user_created",
        "tenant_id",
        "user_id",
        created_at.desc(),
    ),
)


class DocumentElement(Base):
    """Structured table or figure extracted from a PDF."""

    __tablename__ = "document_elements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    document_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("documents.document_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    element_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    element_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "element_type",
            "element_id",
            name="uq_document_element",
        ),
        CheckConstraint(
            "element_type IN ('table', 'figure')",
            name="ck_document_element_type",
        ),
    )