
"""One-time migration of registered documents to Azure embeddings.

Run from the project root:
    python scripts/reindex_azure_embeddings.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.core.config import get_settings
from app.services.ingestion import load_documents
from app.utils.chunking import chunk_documents
from app.storage.document_registry import (
    initialize_registry,
    list_registered_documents,
)
from app.storage.vector_store import (
    get_collection,
    get_document_chunks,
    delete_document_chunks,
    store_chunks,
)


def main():
    settings = get_settings()

    if settings.embedding_provider.strip().lower() != "azure_openai":
        raise RuntimeError(
            "Set EMBEDDING_PROVIDER=azure_openai before migration."
        )

    initialize_registry()

    registered = list_registered_documents()
    ready_documents = [
        item for item in registered
        if item["status"] == "ready"
    ]

    collection = get_collection()

    print("Embedding provider:", settings.embedding_provider)
    print("Target collection:", collection.name)
    print("Ready documents:", len(ready_documents))

    if collection.name != "historical_proposals_azure":
        raise RuntimeError(
            "Refusing migration: unexpected Chroma collection."
        )

    # Prevent accidental indexing into an existing populated collection.
    if collection.count() != 0:
        raise RuntimeError(
            "Azure collection is not empty. "
            "Inspect it before rerunning migration."
        )

    # Validate all source files before generating paid embeddings.
    for record in ready_documents:
        path = settings.upload_dir / record["stored_filename"]

        if not path.is_file():
            raise FileNotFoundError(
                f"Original document missing: {path}"
            )

    migrated = []

    for record in ready_documents:
        document_id = record["document_id"]
        filename = record["filename"]
        stored_filename = record["stored_filename"]
        file_hash = record["file_hash"]

        path = settings.upload_dir / stored_filename

        print(f"\nIndexing: {filename}")

        documents = load_documents(path)

        for document in documents:
            document.metadata.update({
                "document_id": document_id,
                "source_file": filename,
                "stored_filename": stored_filename,
                "file_hash": file_hash,
            })

        chunks = chunk_documents(documents)

        if not chunks:
            raise RuntimeError(
                f"No extractable chunks: {filename}"
            )

        # Ensure every chunk belongs to the expected document.
        if any(
            chunk.metadata.get("document_id") != document_id
            or not chunk.metadata.get("chunk_id")
            for chunk in chunks
        ):
            raise RuntimeError(
                f"Invalid chunk metadata: {filename}"
            )

        try:
            stored_count = store_chunks(chunks)

            indexed = get_document_chunks(document_id)
            actual_count = len(indexed["ids"])

            if actual_count != stored_count:
                raise RuntimeError(
                    f"Chunk count mismatch for {filename}: "
                    f"expected {stored_count}, found {actual_count}"
                )

            print("Indexed chunks:", actual_count)
            migrated.append((document_id, filename))

        except Exception:
            # Clean up partial records for this document.
            # Preserve any original exception.
            try:
                indexed = get_document_chunks(document_id)
                delete_document_chunks(indexed["ids"])
            except Exception as cleanup_error:
                print("Cleanup failed:", cleanup_error)

            raise

    print("\nMigration completed.")
    print("Migrated documents:", len(migrated))
    print("Azure collection chunks:", collection.count())

    for _, filename in migrated:
        print("SUCCESS:", filename)


if __name__ == "__main__":
    main()
