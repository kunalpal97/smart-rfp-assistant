
"""Document ingestion with Azure Document Intelligence and pypdf fallback."""

import logging
from pathlib import Path

from azure.core.exceptions import (
    HttpResponseError,
    ServiceRequestError,
    ServiceResponseError,
)
from langchain_core.documents import Document
from pypdf import PdfReader

from app.core.config import get_settings
from app.integrations.azure_document_intelligence import (
    extract_pdf_with_azure,
)
from app.utils.structured_content import summarize_structured_content


logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

# Only temporary Azure errors should trigger pypdf fallback.
RETRYABLE_HTTP_STATUS_CODES = {408, 429, 500, 502, 503, 504}


def extract_pdf_with_pypdf(
    file_path: Path,
    source: str,
) -> list[Document]:
    """Extract text from each PDF page using pypdf."""

    reader = PdfReader(str(file_path))
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source_file": source,
                    "page": page_number,
                    "extraction_provider": "pypdf",
                },
            )
        )

    if not documents:
        raise ValueError(
            f"No extractable text found in PDF: {source}"
        )

    return documents


def extract_pdf_with_document_intelligence(
    file_path: Path,
    source: str,
    structured_output: dict | None = None,
) -> list[Document]:
    """Extract page text and structured references using Azure.

    Structured output is populated only after successful extraction.
    """

    result = extract_pdf_with_azure(file_path)

    # Extract structured tables and figures from the SAME Azure response.
    # This does not trigger another Azure API request.
    structured = summarize_structured_content(result)

    logger.info(
        "Document layout extracted for %s: %s tables, %s figures",
        source,
        structured["table_count"],
        structured["figure_count"],
    )

    documents = []
    full_content = result.content or ""

    for page in result.pages or []:
        spans = page.spans or []

        if not spans:
            raise ValueError(
                f"Azure returned no content spans for page "
                f"{page.page_number} in {source}"
            )

        parts = []

        for span in spans:
            start = span.offset
            end = start + span.length

            if start < 0 or end > len(full_content):
                raise ValueError(
                    f"Invalid Azure content span on page "
                    f"{page.page_number} in {source}"
                )

            parts.append(full_content[start:end])

        text = "\n".join(parts).strip()

        if not text:
            logger.warning(
                "No text on PDF page %s: %s",
                page.page_number,
                source,
            )
            continue

        # Find tables that belong to this page.
        page_tables = [
            table
            for table in structured["tables"]
            if page.page_number in table["pages"]
        ]

        # Find figures that belong to this page.
        page_figures = [
            figure
            for figure in structured["figures"]
            if page.page_number in figure["pages"]
        ]

        table_ids = ",".join(
            table["table_id"]
            for table in page_tables
        )

        figure_ids = ",".join(
            figure["figure_id"]
            for figure in page_figures
        )

        # Only primitive metadata types are used for ChromaDB.
        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source_file": source,
                    "page": page.page_number,
                    "extraction_provider": "azure_document_intelligence",
                    "table_count": len(page_tables),
                    "figure_count": len(page_figures),
                    "has_table": bool(page_tables),
                    "has_figure": bool(page_figures),
                    "table_ids": table_ids,
                    "figure_ids": figure_ids,
                },
            )
        )

    if not documents:
        raise ValueError(
            f"Azure returned no usable PDF pages: {source}"
        )

    # Publish structured data only after the full extraction succeeds.
    if structured_output is not None:
        structured_output.clear()
        structured_output.update(structured)

    return documents


def extract_pdf(
    file_path: Path,
    source: str,
    structured_output: dict | None = None,
) -> list[Document]:
    """Select configured PDF extractor with controlled Azure fallback."""

    if structured_output is not None:
        structured_output.clear()

    settings = get_settings()
    provider = settings.document_extractor.strip().lower()

    if provider == "pypdf":
        return extract_pdf_with_pypdf(file_path, source)

    if provider != "azure_document_intelligence":
        raise ValueError(
            f"Unsupported document extractor: {provider}"
        )

    try:
        return extract_pdf_with_document_intelligence(
            file_path,
            source,
            structured_output=structured_output,
        )

    except HttpResponseError as exc:
        if exc.status_code not in RETRYABLE_HTTP_STATUS_CODES:
            logger.exception(
                "Non-retryable Azure extraction error for %s",
                source,
            )
            raise

        logger.warning(
            "Temporary Azure HTTP error (%s) for %s. "
            "Attempting pypdf fallback.",
            exc.status_code,
            source,
        )

    except (ServiceRequestError, ServiceResponseError):
        logger.warning(
            "Azure Document Intelligence connection failure "
            "for %s. Attempting pypdf fallback.",
            source,
            exc_info=True,
        )

    # Do not expose structured data from a failed Azure extraction.
    if structured_output is not None:
        structured_output.clear()

    # Fallback must still extract real text.
    # Scanned PDFs may not be recoverable using pypdf.
    return extract_pdf_with_pypdf(file_path, source)


def extract_text_file(
    file_path: Path,
    source: str,
) -> list[Document]:
    """Extract UTF-8 content from TXT and Markdown files."""

    text = file_path.read_text(encoding="utf-8-sig")

    if not text.strip():
        raise ValueError(
            f"Text file is empty: {source}"
        )

    return [
        Document(
            page_content=text,
            metadata={
                "source_file": source,
                "page": "N/A",
                "extraction_provider": "utf8",
            },
        )
    ]


def load_documents(
    path: str | Path,
    structured_output: dict | None = None,
) -> list[Document]:
    """Load supported documents from a file or directory.

    Structured output is supported for a single PDF file.
    Existing callers remain compatible.
    """

    if structured_output is not None:
        structured_output.clear()

    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Path not found: {root}"
        )

    if root.is_file():
        files = [root]
        base_dir = root.parent
    else:
        files = sorted(
            p for p in root.rglob("*") if p.is_file()
        )
        base_dir = root

    documents = []

    for file_path in files:
        extension = file_path.suffix.lower()

        if extension not in SUPPORTED_EXTENSIONS:
            continue

        source = file_path.relative_to(base_dir).as_posix()

        if extension == ".pdf":
            # Collect structured output only for a single PDF.
            # Do not mix metadata from multiple PDFs.
            output_target = (
                structured_output
                if len(files) == 1
                else None
            )

            extracted = extract_pdf(
                file_path,
                source,
                structured_output=output_target,
            )

        else:
            extracted = extract_text_file(
                file_path,
                source,
            )

        documents.extend(extracted)

    return documents
