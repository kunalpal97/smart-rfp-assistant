from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.permissions import require_admin, require_user

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


@router.post(
    "/upload",
    dependencies=[Depends(require_admin)],
)
def upload_document(
    file: UploadFile = File(...),
):
    """Upload and index a historical proposal. Admin only."""

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


@router.get(
    "",
    dependencies=[Depends(require_user)],
)
def list_documents():
    """List indexed historical proposals. User or Admin."""

    return list_documents_service()


@router.delete(
    "/{document_id}",
    dependencies=[Depends(require_admin)],
)
def delete_document(
    document_id: str,
):
    """Delete a document and its indexed chunks. Admin only."""

    try:
        return delete_document_service(document_id)
    except DocumentError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc