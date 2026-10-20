
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_service import (
    DocumentError,
    delete_document as delete_document_service,
    list_documents as list_documents_service,
    upload_document as upload_document_service,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    """Upload and index a historical proposal."""

    # Read at most 10 MB + 1 byte.
    content = file.file.read(10 * 1024 * 1024 + 1)

    try:
        return upload_document_service(
            filename=file.filename or "",
            content=content,
        )
    except DocumentError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc


@router.get("")
def list_documents():
    """List indexed historical proposals."""

    return list_documents_service()


@router.delete("/{document_id}")
def delete_document(document_id: str):
    """Delete a document and its indexed chunks."""

    try:
        return delete_document_service(document_id)
    except DocumentError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
