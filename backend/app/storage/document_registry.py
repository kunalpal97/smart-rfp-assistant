
"""Document registry repository using SQLAlchemy.

Supports SQLite during local development and PostgreSQL after migration.
Document metadata is shared across users and managed by admins.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.storage.db_engine import engine, get_db_session
from app.storage.models import Base, Document

logger = logging.getLogger(__name__)

VALID_STATUSES = {"processing", "ready", "failed"}
VALID_STORAGE_PROVIDERS = {"local", "azure_blob"}


def _utc_now() -> str:
    """Return a UTC timestamp compatible with the existing database."""
    return datetime.now(timezone.utc).isoformat()


def _document_to_dict(document: Document) -> dict:
    """Convert a SQLAlchemy document model to a plain dictionary."""
    return {
        column.name: getattr(document, column.name)
        for column in Document.__table__.columns
    }


def initialize_registry() -> None:
    """Ensure the document table exists.

    This preserves the existing schema for the transition period.
    Alembic will manage schema migrations in production.
    """
    Base.metadata.create_all(
        bind=engine,
        tables=[Document.__table__],
        checkfirst=True,
    )


def create_document(
    document_id: str,
    filename: str,
    stored_filename: str,
    file_hash: str,
    storage_provider: str = "local",
) -> None:
    """Register a document with initial processing status."""

    if storage_provider not in VALID_STORAGE_PROVIDERS:
        raise ValueError(
            f"Unsupported storage provider: {storage_provider}"
        )

    now = _utc_now()

    document = Document(
        document_id=document_id,
        filename=filename,
        stored_filename=stored_filename,
        file_hash=file_hash,
        status="processing",
        chunk_count=0,
        error_message=None,
        created_at=now,
        updated_at=now,
        storage_provider=storage_provider,
    )

    with get_db_session() as session:
        session.add(document)
        session.flush()


def update_document_status(
    document_id: str,
    status: str,
    chunk_count: int = 0,
    error_message: str | None = None,
) -> None:
    """Update document processing status."""

    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid document status: {status}")

    if chunk_count < 0:
        raise ValueError("Chunk count cannot be negative.")

    with get_db_session() as session:
        document = session.get(Document, document_id)

        if document is None:
            raise ValueError(
                f"Document not found: {document_id}"
            )

        document.status = status
        document.chunk_count = chunk_count
        document.error_message = error_message
        document.updated_at = _utc_now()


def find_document_by_hash(file_hash: str) -> dict | None:
    """Find a document using its SHA256 file hash."""

    with get_db_session() as session:
        document = session.scalar(
            select(Document).where(
                Document.file_hash == file_hash
            )
        )

        return (
            _document_to_dict(document)
            if document is not None
            else None
        )


def list_registered_documents() -> list[dict]:
    """Return all registered documents, newest first."""

    with get_db_session() as session:
        documents = session.scalars(
            select(Document).order_by(
                Document.created_at.desc()
            )
        ).all()

        return [
            _document_to_dict(document)
            for document in documents
        ]


def get_registered_document(document_id: str) -> dict | None:
    """Find a document using its primary key."""

    with get_db_session() as session:
        document = session.get(Document, document_id)

        return (
            _document_to_dict(document)
            if document is not None
            else None
        )


def delete_registered_document(document_id: str) -> None:
    """Delete a document registry entry.

    Missing records are treated as already deleted.
    """

    with get_db_session() as session:
        document = session.get(Document, document_id)

        if document is not None:
            session.delete(document)


def import_existing_documents() -> int:
    """Import legacy indexed document metadata from ChromaDB.

    Existing registered documents are not overwritten.
    """

    from app.storage.vector_store import get_collection

    initialize_registry()

    results = get_collection().get(
        include=["metadatas"]
    )

    unique_documents: dict[str, dict] = {}

    for metadata in results.get("metadatas", []):
        if not metadata:
            continue

        document_id = metadata.get("document_id")

        if not document_id:
            continue

        if document_id not in unique_documents:
            unique_documents[document_id] = {
                "filename": metadata.get("source_file"),
                "stored_filename": metadata.get("stored_filename"),
                "file_hash": metadata.get("file_hash"),
                "storage_provider": metadata.get(
                    "storage_provider", "local"
                ),
                "chunk_count": 0,
            }

        unique_documents[document_id]["chunk_count"] += 1

    imported_count = 0

    for document_id, metadata in unique_documents.items():

        if not all([
            metadata["filename"],
            metadata["stored_filename"],
            metadata["file_hash"],
        ]):
            continue

        provider = metadata["storage_provider"]

        if provider not in VALID_STORAGE_PROVIDERS:
            logger.warning(
                "Skipping legacy document %s: invalid provider",
                document_id,
            )
            continue

        now = _utc_now()

        try:
            with get_db_session() as session:

                existing = session.get(
                    Document, document_id
                )

                if existing is not None:
                    continue

                document = Document(
                    document_id=document_id,
                    filename=metadata["filename"],
                    stored_filename=metadata["stored_filename"],
                    file_hash=metadata["file_hash"],
                    status="ready",
                    chunk_count=metadata["chunk_count"],
                    error_message=None,
                    created_at=now,
                    updated_at=now,
                    storage_provider=provider,
                )

                session.add(document)
                session.flush()

            imported_count += 1

        except IntegrityError:
            # Another record may already have this hash,
            # or a concurrent import may have inserted it.
            logger.info(
                "Skipping already registered legacy document %s",
                document_id,
            )

    return imported_count
