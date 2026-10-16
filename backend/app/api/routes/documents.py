
from pathlib import Path
from uuid import uuid4
import hashlib

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.storage.vector_store import get_collection

from app.services.ingestion import load_documents
from app.utils.chunking import chunk_documents
from app.storage.vector_store import store_chunks


router = APIRouter(prefix="/api/documents", tags=["Documents"])

PROJECT_ROOT = Path(__file__).resolve().parents[4]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB



@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    # 1. Validate supported file type.
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT and MD files are supported.",
        )

    # 2. Validate file size.
    content = file.file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must not exceed 10 MB.",
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # 3. Calculate SHA-256 hash BEFORE saving the file.
    file_hash = hashlib.sha256(content).hexdigest()

    # 4. Check for duplicate content in ChromaDB.
    collection = get_collection()

    existing = collection.get(
        where={"file_hash": file_hash},
        include=["metadatas"],
        limit=1,
    )

    if existing["ids"]:
        existing_metadata = existing["metadatas"][0]

        raise HTTPException(
            status_code=409,
            detail={
                "message": "This document has already been uploaded.",
                "existing_document_id": existing_metadata.get(
                    "document_id"
                ),
                "existing_filename": existing_metadata.get(
                    "source_file"
                ),
            },
        )

    # 5. Generate a unique ID and save the file.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    document_id = uuid4().hex
    stored_filename = f"{document_id}{extension}"
    saved_path = UPLOAD_DIR / stored_filename

    try:
        saved_path.write_bytes(content)

        # 6. Extract text from the uploaded file.
        documents = load_documents(saved_path)

        # 7. Attach document metadata.
        for document in documents:
            document.metadata["document_id"] = document_id
            document.metadata["source_file"] = filename
            document.metadata["stored_filename"] = stored_filename
            document.metadata["file_hash"] = file_hash

        # 8. Split text into chunks.
        chunks = chunk_documents(documents)

        if not chunks:
            raise ValueError("No extractable text found.")

        # 9. Generate embeddings and store in ChromaDB.
        stored_count = store_chunks(chunks)

        return {
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            "original_filename": filename,
            "stored_filename": stored_filename,
            "chunks_created": stored_count,
        }

    except Exception:
        saved_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail="Document could not be processed.",
        )



@router.get("")
def list_documents():
    """List uploaded documents indexed in ChromaDB."""

    collection = get_collection()

    results = collection.get(include=["metadatas"])

    documents = {}

    for metadata in results["metadatas"]:
        if not metadata:
            continue

        document_id = metadata.get("document_id")

        # Skip legacy records without a document ID.
        if not document_id:
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


@router.delete("/{document_id}")
def delete_document(document_id: str):
    collection = get_collection()

    results = collection.get(
        where={"document_id": document_id},
        include=["metadatas"],
    )

    if not results["ids"]:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    metadata = results["metadatas"][0]
    stored_filename = metadata.get("stored_filename")

    if not stored_filename:
        raise HTTPException(
            status_code=422,
            detail="Stored filename missing.",
        )

    file_path = UPLOAD_DIR / stored_filename

    collection.delete(ids=results["ids"])
    file_path.unlink(missing_ok=True)

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
        "chunks_deleted": len(results["ids"]),
    }
