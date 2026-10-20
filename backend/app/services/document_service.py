
import hashlib
import sqlite3
from pathlib import Path
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)

from app.core.config import get_settings
from app.services.ingestion import load_documents
from app.storage.document_registry import (
    create_document,
    delete_registered_document,
    find_document_by_hash as find_registered_by_hash,
    get_registered_document,
    initialize_registry,
    list_registered_documents,
    update_document_status,
)
from app.storage.vector_store import (
    delete_document_chunks,
    find_document_by_hash as find_indexed_by_hash,
    get_collection,
    get_document_chunks,
    store_chunks,
)
from app.utils.chunking import chunk_documents


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024


class DocumentError(Exception):
    """Expected document-processing error."""

    def __init__(
        self,
        message: str | dict,
        status_code: int = 400,
    ):
        self.message = message
        self.status_code = status_code
        super().__init__(str(message))


def upload_document(filename: str, content: bytes) -> dict:
    """Register, process and index an uploaded document."""

    filename = Path(filename).name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise DocumentError(
            "Only PDF, TXT and MD files are supported.", 400
        )

    if len(content) > MAX_FILE_SIZE:
        raise DocumentError(
            "File size must not exceed 10 MB.", 413
        )

    if not content:
        raise DocumentError("Uploaded file is empty.", 400)

    initialize_registry()

    file_hash = hashlib.sha256(content).hexdigest()

    # Check both stores while legacy documents are being migrated.
    existing = find_registered_by_hash(file_hash)

    if existing and existing["status"] == "failed":
        delete_registered_document(existing["document_id"])
        existing = None

    if existing:
        raise DocumentError(
            {
                "message": "This document has already been uploaded.",
                "existing_document_id": existing["document_id"],
                "existing_filename": existing["filename"],
            },
            409,
        )

    indexed = find_indexed_by_hash(file_hash)

    if indexed:
        raise DocumentError(
            {
                "message": "This document has already been uploaded.",
                "existing_document_id": indexed.get("document_id"),
                "existing_filename": indexed.get("source_file"),
            },
            409,
        )

    document_id = uuid4().hex
    stored_filename = f"{document_id}{extension}"

    upload_dir = get_settings().upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / stored_filename

    try:
        # SQLite UNIQUE(file_hash) protects against concurrent duplicates.
        create_document(
            document_id,
            filename,
            stored_filename,
            file_hash,
        )
    except sqlite3.IntegrityError as exc:
        existing = find_registered_by_hash(file_hash)
        raise DocumentError(
            {
                "message": "This document has already been uploaded.",
                "existing_document_id": (
                    existing["document_id"] if existing else None
                ),
                "existing_filename": (
                    existing["filename"] if existing else None
                ),
            },
            409,
        ) from exc

    try:
        saved_path.write_bytes(content)

        documents = load_documents(saved_path)

        for document in documents:
            document.metadata.update({
                "document_id": document_id,
                "source_file": filename,
                "stored_filename": stored_filename,
                "file_hash": file_hash,
            })

        chunks = chunk_documents(documents)

        if not chunks:
            raise ValueError("No extractable text found.")

        stored_count = store_chunks(chunks)

        update_document_status(
            document_id,
            status="ready",
            chunk_count=stored_count,
        )

        return {
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            "original_filename": filename,
            "stored_filename": stored_filename,
            "chunks_created": stored_count,
        }

    except Exception as exc:
        # Attempt to remove partially indexed chunks.

        logger.exception(
            "Document processing failed for %s",
            filename,
        )
        try:
            results = get_document_chunks(document_id)
            delete_document_chunks(results["ids"])
        except Exception:
            pass

        saved_path.unlink(missing_ok=True)

        update_document_status(
            document_id,
            status="failed",
            error_message=str(exc),
        )

        raise DocumentError(
            "Document could not be processed.", 422
        ) from exc



def list_documents() -> dict:
    """List ready documents and unmigrated legacy documents."""

    initialize_registry()

    registered = list_registered_documents()
    registered_ids = {
        item["document_id"] for item in registered
    }

    documents = {
        item["document_id"]: {
            "document_id": item["document_id"],
            "filename": item["filename"],
            "stored_filename": item["stored_filename"],
            "chunk_count": item["chunk_count"],
        }
        for item in registered
        if item["status"] == "ready"
    }

    # Temporary support for legacy ChromaDB documents.
    results = get_collection().get(include=["metadatas"])

    for metadata in results["metadatas"]:
        if not metadata:
            continue

        document_id = metadata.get("document_id")

        # Never expose failed/processing registered documents.
        if not document_id or document_id in registered_ids:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata.get("source_file"),
                "stored_filename": metadata.get("stored_filename"),
                "chunk_count": 0,
            }

        documents[document_id]["chunk_count"] += 1

    return {
        "total_documents": len(documents),
        "documents": list(documents.values()),
    }


def delete_document(document_id: str) -> dict:
    """Delete a document from ChromaDB, local storage and SQLite."""

    initialize_registry()

    registered = get_registered_document(document_id)
    results = get_document_chunks(document_id)

    if not registered and not results["ids"]:
        raise DocumentError("Document not found.", 404)

    metadata = (
        results["metadatas"][0]
        if results["ids"]
        else {}
    )

    stored_filename = (
        registered["stored_filename"]
        if registered
        else metadata.get("stored_filename")
    )

    if not stored_filename:
        raise DocumentError("Stored filename missing.", 422)

    file_path = get_settings().upload_dir / stored_filename

    delete_document_chunks(results["ids"])
    file_path.unlink(missing_ok=True)

    if registered:
        delete_registered_document(document_id)

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "chunks_deleted": len(results["ids"]),
    }
