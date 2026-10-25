
from collections import defaultdict

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.content_types import detect_content_type


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[Document]:
    """Split documents into chunks and attach stable chunk IDs."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            r"(?m:^#{1,6}[ \t]+)",
            r"\n\n",
            r"\n",
            r"\. ",
            r" ",
            r"",
        ],
        keep_separator="start",
        is_separator_regex=True,
    )


    chunks = splitter.split_documents(documents)

    counters = defaultdict(int)

    for chunk in chunks:
        source = chunk.metadata["source_file"]
        page = chunk.metadata["page"]

        document_id = chunk.metadata.get("document_id", source)

        # Keep the existing document/page-based chunk identity.
        key = (document_id, str(page))
        counters[key] += 1

        chunk.metadata["chunk_id"] = (
            f"{document_id}::page-{page}::chunk-{counters[key]:03d}"
        )

        # Classify the extracted chunk for indexing and UI metadata.
        # This is heuristic classification, not structured table parsing.
        chunk.metadata["content_type"] = detect_content_type(
            chunk.page_content
        )

    return chunks
