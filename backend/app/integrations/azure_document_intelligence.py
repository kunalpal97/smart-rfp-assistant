
from functools import lru_cache
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentContentFormat
from azure.core.credentials import AzureKeyCredential

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_document_intelligence_client() -> DocumentIntelligenceClient:
    settings = get_settings()

    endpoint = settings.azure_document_intelligence_endpoint.strip()
    key = settings.azure_document_intelligence_key.strip()

    if not endpoint or not key:
        raise ValueError(
            "Azure Document Intelligence endpoint or key is missing."
        )

    return DocumentIntelligenceClient(
        endpoint=endpoint.rstrip("/"),
        credential=AzureKeyCredential(key),
    )


def extract_pdf_with_azure(file_path: str | Path):
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Azure PDF extractor requires a PDF file.")

    client = get_document_intelligence_client()

    with path.open("rb") as file:
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=file,
            output_content_format=DocumentContentFormat.MARKDOWN,
        )

    result = poller.result()

    if not result.pages or not (result.content or "").strip():
        raise ValueError(
            "Azure Document Intelligence returned no extractable content."
        )

    return result
