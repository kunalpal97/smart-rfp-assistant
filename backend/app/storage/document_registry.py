
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import get_settings


def get_database_path() -> Path:
    """Return the local SQLite registry path."""
    return get_settings().chroma_dir.parent / "documents.db"


@contextmanager
def get_connection():
    """Create and close a SQLite connection."""

    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        db_path,
        timeout=30,
    )
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_registry() -> None:
    """Create the document registry table if needed."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                file_hash TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL
                    CHECK(status IN ('processing', 'ready', 'failed')),
                chunk_count INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


def create_document(
    document_id: str,
    filename: str,
    stored_filename: str,
    file_hash: str,
) -> None:
    """Register a document before processing."""

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_id,
                filename,
                stored_filename,
                file_hash,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, 'processing', ?, ?)
            """,
            (
                document_id,
                filename,
                stored_filename,
                file_hash,
                now,
                now,
            ),
        )


def update_document_status(
    document_id: str,
    status: str,
    chunk_count: int = 0,
    error_message: str | None = None,
) -> None:
    """Update document processing status."""

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE documents
            SET status = ?,
                chunk_count = ?,
                error_message = ?,
                updated_at = ?
            WHERE document_id = ?
            """,
            (
                status,
                chunk_count,
                error_message,
                now,
                document_id,
            ),
        )


def find_document_by_hash(file_hash: str) -> dict | None:
    """Find an existing registered document by its hash."""

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM documents WHERE file_hash = ?",
            (file_hash,),
        ).fetchone()

    return dict(row) if row else None


def list_registered_documents() -> list[dict]:
    """Return all registered documents."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM documents
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def delete_registered_document(document_id: str) -> None:
    """Remove a document's registry record."""

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM documents WHERE document_id = ?",
            (document_id,),
        )




def import_existing_documents() -> int:
    """Import existing indexed document metadata into SQLite."""

    from app.storage.vector_store import get_collection

    initialize_registry()

    results = get_collection().get(include=["metadatas"])

    unique_documents = {}

    for metadata in results["metadatas"]:
        if not metadata:
            continue

        document_id = metadata.get("document_id")

        # Older mock proposal chunks may not have document IDs.
        if not document_id:
            continue

        if document_id not in unique_documents:
            unique_documents[document_id] = {
                "filename": metadata.get("source_file"),
                "stored_filename": metadata.get("stored_filename"),
                "file_hash": metadata.get("file_hash"),
                "chunk_count": 0,
            }

        unique_documents[document_id]["chunk_count"] += 1

    imported_count = 0
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        for document_id, metadata in unique_documents.items():
            # Skip records without required metadata.
            if not all([
                metadata["filename"],
                metadata["stored_filename"],
                metadata["file_hash"],
            ]):
                continue

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO documents (
                    document_id,
                    filename,
                    stored_filename,
                    file_hash,
                    status,
                    chunk_count,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 'ready', ?, ?, ?)
                """,
                (
                    document_id,
                    metadata["filename"],
                    metadata["stored_filename"],
                    metadata["file_hash"],
                    metadata["chunk_count"],
                    now,
                    now,
                ),
            )

            imported_count += cursor.rowcount

    return imported_count



def get_registered_document(document_id: str) -> dict | None:
    """Find a registered document by its ID."""

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM documents WHERE document_id = ?",
            (document_id,),
        ).fetchone()

    return dict(row) if row else None
