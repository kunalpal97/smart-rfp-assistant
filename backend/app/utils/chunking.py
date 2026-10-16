
from collections import defaultdict

from langchain_core.documents import Document # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[Document]:
    """Split documents into chunks and attach stable chunk IDs."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = splitter.split_documents(documents)
    counters = defaultdict(int)

    
    for chunk in chunks:
        source = chunk.metadata["source_file"]
        page = chunk.metadata["page"]

        # Uploaded documents have an internal ID.
        # Historical mock files may not have one yet.
        document_id = chunk.metadata.get("document_id", source)

        key = (document_id, str(page))
        counters[key] += 1

        chunk.metadata["chunk_id"] = (
            f"{document_id}::page-{page}::chunk-{counters[key]:03d}"
        )


    return chunks