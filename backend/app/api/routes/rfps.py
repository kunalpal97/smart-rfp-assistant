
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.rfp_service import (
    RFPProcessingError,
    extract_rfp_text,
)


router = APIRouter(
    prefix="/api/rfps",
    tags=["Customer RFPs"],
)


@router.post("/extract")
def extract_customer_rfp(file: UploadFile = File(...)):
    """
    Upload a customer RFP and extract its text.

    Does not index the uploaded RFP into ChromaDB.
    """

    # Read at most 10 MB + 1 byte.
    content = file.file.read(10 * 1024 * 1024 + 1)

    try:
        return extract_rfp_text(
            filename=file.filename or "",
            content=content,
        )

    except RFPProcessingError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
