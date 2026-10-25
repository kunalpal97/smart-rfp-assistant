
import hashlib
import logging
import tempfile
import time

from sqlalchemy.exc import IntegrityError
from pathlib import Path
from uuid import uuid4

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
from app.storage.file_storage import (
    delete_file,
    get_storage_provider,
    save_file,
)
from app.storage.vector_store import (
    delete_document_chunks,
    delete_document_from_all_collections,
    find_document_by_hash as find_indexed_by_hash,
    get_collection,
    get_document_chunks,
    store_chunks,
)
from app.storage.structured_content_repository import (
    delete_document_elements,
    save_document_elements,
)
from app.utils.chunking import chunk_documents

from app.core.config import get_settings
from app.storage.azure_search_store import (
    index_chunks,
    delete_document_from_search,
)

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024

# ENABLE_UPLOAD_PERFORMANCE_LOGS = False

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
    """Register, store, process and index an uploaded document."""

    total_start = time.perf_counter()

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

    # Measure hashing and duplicate checks.
    prepare_start = time.perf_counter()

    initialize_registry()

    file_hash = hashlib.sha256(content).hexdigest()

    existing = find_registered_by_hash(file_hash)

    if existing and existing["status"] == "failed":
        raise DocumentError(
            {
                "message": (
                    "A previous upload of this document failed. "
                    "Resolve or clean up that record before retrying."
                ),
                "existing_document_id": existing["document_id"],
                "existing_filename": existing["filename"],
            },
            409,
        )

    if existing:
        raise DocumentError(
            {
                "message": "This document has already been uploaded.",
                "existing_document_id": existing["document_id"],
                "existing_filename": existing["filename"],
            },
            409,
        )

    # Preserve legacy ChromaDB duplicate detection.
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

    prepare_time = time.perf_counter() - prepare_start

    document_id = uuid4().hex
    stored_filename = f"{document_id}{extension}"
    storage_provider = get_storage_provider()

    # Register the document exactly once.
    try:
        registry_start = time.perf_counter()

        create_document(
            document_id,
            filename,
            stored_filename,
            file_hash,
            storage_provider=storage_provider,
        )

        registry_time = time.perf_counter() - registry_start

    except IntegrityError as exc:
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
        # Measure local or Azure Blob upload.
        storage_start = time.perf_counter()

        save_file(
            stored_filename,
            content,
            storage_provider,
        )

        storage_time = time.perf_counter() - storage_start

        # Create temporary file for existing extraction logic.
        with tempfile.TemporaryDirectory(
            prefix="rfp-extract-"
        ) as temp_dir:
            temporary_path = Path(temp_dir) / stored_filename

            temp_start = time.perf_counter()
            temporary_path.write_bytes(content)
            temp_write_time = time.perf_counter() - temp_start

            # Measure PDF/TXT/MD extraction.
            extraction_start = time.perf_counter()
            # Collect structured tables and figures from the same extraction.
            structured_content = {}

            documents = load_documents(
                temporary_path,
                structured_output=structured_content,
            )
            extraction_time = time.perf_counter() - extraction_start

        # Preserve original metadata for RAG citations.
        for document in documents:
            document.metadata.update({
                "document_id": document_id,
                "source_file": filename,
                "stored_filename": stored_filename,
                "file_hash": file_hash,
            })

        # Measure chunking.
        chunk_start = time.perf_counter()

        chunks = chunk_documents(documents)

        chunk_time = time.perf_counter() - chunk_start

        if not chunks:
            raise ValueError("No extractable text found.")

        # Measure embeddings and ChromaDB indexing together.
        index_start = time.perf_counter()

        stored_count = store_chunks(chunks)

        index_time = time.perf_counter() - index_start

        # Save structured tables and figures in PostgreSQL.
        # For TXT/MD or pypdf fallback, the lists will be empty.
        structured_count = save_document_elements(
            document_id=document_id,
            structured=structured_content,
        )

        logger.info(
            "Stored %s structured elements for document %s",
            structured_count,
            document_id,
        )



        # Mark the primary (ChromaDB + PostgreSQL) upload as ready.
        status_start = time.perf_counter()
        update_document_status(
            document_id,
            status="ready",
            chunk_count=stored_count,
        )
        status_time = time.perf_counter() - status_start

        # Best-effort Azure AI Search indexing during migration.
        # Azure failures are logged but do not invalidate the primary upload.
        azure_search_indexed = False
        azure_search_time = 0.0

        if get_settings().azure_search_enabled:
            azure_start = time.perf_counter()
            try:
                azure_count = index_chunks(chunks)
                if azure_count != len(chunks):
                    raise RuntimeError(
                        f"Azure indexed {azure_count}/{len(chunks)} chunks."
                    )

                azure_search_indexed = True
                logger.info(
                    "Azure AI Search indexed %s chunks for document %s",
                    azure_count,
                    document_id,
                )
            except Exception:
                logger.exception(
                    "Azure AI Search indexing failed for document %s; "
                    "the ChromaDB upload remains ready.",
                    document_id,
                )
            finally:
                azure_search_time = time.perf_counter() - azure_start
                logger.info(
                    "Azure AI Search indexing duration: %.3f seconds",
                    azure_search_time,
                )

        total_time = time.perf_counter() - total_start

        # if ENABLE_UPLOAD_PERFORMANCE_LOGS:
        # Report successful upload performance.
        # logger.warning(
        #     "\n"
        #     "========== DOCUMENT UPLOAD PERFORMANCE ==========\n"
        #     "Document       : %s\n"
        #     "Provider       : %s\n"
        #     "Size           : %.2f KiB\n"
        #     "Chunks         : %d\n"
        #     "Prepare        : %.3f s\n"
        #     "Registry register: %.3f s\n"
        #     "Storage upload : %.3f s\n"
        #     "Temp file write: %.3f s\n"
        #     "Extraction     : %.3f s\n"
        #     "Chunking       : %.3f s\n"
        #     "Embedding+Index: %.3f s\n"
        #     "Registry update  : %.3f s\n"
        #     "TOTAL          : %.3f s\n"
        #     "=================================================",
        #     filename,
        #     storage_provider,
        #     len(content) / 1024,
        #     stored_count,
        #     prepare_time,
        #     registry_time,
        #     storage_time,
        #     temp_write_time,
        #     extraction_time,
        #     chunk_time,
        #     index_time,
        #     status_time,
        #     total_time,
        # )

        return {
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            "original_filename": filename,
            "stored_filename": stored_filename,
            "chunks_created": stored_count,
            "structured_elements_created": structured_count,
            "azure_search_indexed": azure_search_indexed,
        }

    except Exception as exc:
        logger.exception(
            "Document processing failed for %s",
            filename,
        )

        # Remove partially indexed chunks.
        try:
            results = get_document_chunks(document_id)
            delete_document_chunks(results["ids"])
        except Exception:
            logger.exception(
                "Failed to clean up indexed chunks for %s",
                document_id,
            )

        # Remove structured elements if upload processing fails.
        try:
            delete_document_elements(document_id)
        except Exception:
            logger.exception(
                "Failed to clean up structured elements for %s",
                document_id,
            )

        # Remove original file from its recorded provider.
        try:
            delete_file(stored_filename, storage_provider)
        except Exception:
            logger.exception(
                "Failed to clean up stored file for %s",
                document_id,
            )

        # Keep failed record for troubleshooting.
        try:
            update_document_status(
                document_id,
                status="failed",
                error_message=str(exc),
            )
        except Exception:
            logger.exception(
                "Failed to update document status for %s",
                document_id,
            )

        logger.warning(
            "Document upload FAILED: %s | Provider: %s | "
            "Elapsed: %.3f s",
            filename,
            storage_provider,
            time.perf_counter() - total_start,
        )

        raise DocumentError(
            "Document could not be processed.", 422
        ) from exc



def list_documents() -> dict:
    """List all registered documents with their processing status.

    Includes ready, processing and failed documents.
    Preserves compatibility with unmigrated legacy ChromaDB entries.
    """

    initialize_registry()

    registered = list_registered_documents()

    registered_ids = {
        item["document_id"] for item in registered
    }

    documents = {}

    # Include every registered document, regardless of status.
    for item in registered:
        document_id = item["document_id"]

        documents[document_id] = {
            "document_id": document_id,
            "filename": item["filename"],
            "stored_filename": item["stored_filename"],
            "chunk_count": item["chunk_count"],
            "status": item["status"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "error_message": item["error_message"],
            "storage_provider": item["storage_provider"],
        }

    # Preserve unmigrated legacy ChromaDB documents.
    results = get_collection().get(include=["metadatas"])

    for metadata in results["metadatas"]:
        if not metadata:
            continue

        document_id = metadata.get("document_id")

        if not document_id or document_id in registered_ids:
            continue

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata.get("source_file") or "Unknown document",
                "stored_filename": metadata.get("stored_filename"),
                "chunk_count": 0,
                "status": "legacy",
                "created_at": None,
                "updated_at": None,
                "error_message": None,
                "storage_provider": "local",
            }

        documents[document_id]["chunk_count"] += 1

    return {
        "total_documents": len(documents),
        "documents": list(documents.values()),
    }


def delete_document(document_id: str) -> dict:
    """Delete document from storage, indexes and PostgreSQL."""

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
        raise DocumentError(
            "Stored filename missing.", 422
        )

    # Use recorded provider to support old local documents.
    storage_provider = (
        registered.get("storage_provider", "local")
        if registered
        else "local"
    )

    # Delete Azure AI Search chunks before removing the source records.
    # Do not silently continue if deletion fails.
    if get_settings().azure_search_enabled:
        azure_deleted = delete_document_from_search(document_id)

        logger.info(
            "Deleted %s Azure AI Search chunks for document %s",
            azure_deleted,
            document_id,
        )

    # Delete original document.
    delete_file(stored_filename, storage_provider)

    # Preserve deletion across ChromaDB collections.
    chunks_deleted = delete_document_from_all_collections(
        document_id
    )

    # Delete structured content before removing the parent registry row.
    # PostgreSQL ON DELETE CASCADE is an additional safety net.
    delete_document_elements(document_id)

    # Delete registry record last.
    if registered:
        delete_registered_document(document_id)

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "chunks_deleted": chunks_deleted,
    }
