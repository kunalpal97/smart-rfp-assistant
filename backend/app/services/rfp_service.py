
from pathlib import Path
from tempfile import TemporaryDirectory

from app.services.ingestion import load_documents
from app.services.rfp_extraction import extract_questions


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024


class RFPProcessingError(Exception):
    """Expected error while processing a customer RFP."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def extract_rfp_text(filename: str, content: bytes) -> dict:
    """
    Validate a customer RFP and extract its text.

    Customer RFPs are NOT added to ChromaDB.
    """

    safe_filename = Path(filename).name
    extension = Path(safe_filename).suffix.lower()

    # 1. Validate file type.
    if extension not in ALLOWED_EXTENSIONS:
        raise RFPProcessingError(
            "Only PDF, TXT and MD files are supported."
        )

    # 2. Validate file size.
    if len(content) > MAX_FILE_SIZE:
        raise RFPProcessingError(
            "File size must not exceed 10 MB.",
            status_code=413,
        )

    # 3. Reject empty files.
    if not content:
        raise RFPProcessingError(
            "Uploaded RFP file is empty."
        )

    # 4. Temporarily save the file.
    with TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / f"customer_rfp{extension}"
        file_path.write_bytes(content)

        try:
            # Reuse your existing PDF/TXT/MD loader.
            documents = load_documents(file_path)
        except Exception as exc:
            raise RFPProcessingError(
                "Unable to extract text from the uploaded RFP.",
                status_code=422,
            ) from exc

    # 5. Combine extracted pages into one text.
    full_text = "\n\n".join(
        document.page_content
        for document in documents
        if document.page_content.strip()
    )

    if not full_text.strip():
        raise RFPProcessingError(
            "No extractable text found in the RFP.",
            status_code=422,
        )

    questions = extract_questions(full_text)

    return {
        "filename": safe_filename,
        "page_count": len(documents),
        "character_count": len(full_text),
        "text": full_text,
        "total_questions": len(questions),
        "questions": questions,
    }
