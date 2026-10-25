
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.core.config import get_settings
from app.integrations.azure_document_intelligence import (
    extract_pdf_with_azure,
)


def main():
    settings = get_settings()

    # Use the original uploaded PDF already registered in SQLite.
    from app.storage.document_registry import (
        list_registered_documents,
    )

    pdf_records = [
        doc
        for doc in list_registered_documents()
        if doc["status"] == "ready"
        and doc["filename"].lower().endswith(".pdf")
    ]

    if not pdf_records:
        raise RuntimeError("No registered PDF available for testing.")

    record = pdf_records[0]
    path = settings.upload_dir / record["stored_filename"]

    print("Testing:", record["filename"])

    result = extract_pdf_with_azure(path)

    print("Model:", result.model_id)
    print("Pages:", len(result.pages))
    print("Tables:", len(result.tables or []))
    print("Extracted characters:", len(result.content or ""))

    for page in result.pages:
        print("Page:", page.page_number)

    print("\n--- Extracted preview ---")
    print((result.content or "")[:2500])


if __name__ == "__main__":
    main()
