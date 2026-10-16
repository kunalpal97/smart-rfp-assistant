
from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


def load_documents(path: str | Path) -> list[Document]:
    root = Path(path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    if root.is_file():
        files = [root]
        base_dir = root.parent
    else:
        files = sorted(p for p in root.rglob("*") if p.is_file())
        base_dir = root

    documents = []

    for file_path in files:
        extension = file_path.suffix.lower()

        if extension not in {".pdf", ".txt", ".md"}:
            continue

        source = file_path.relative_to(base_dir).as_posix()

        if extension == ".pdf":
            reader = PdfReader(str(file_path))

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""

                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source_file": source,
                                "page": page_number,
                            },
                        )
                    )

        else:
            text = file_path.read_text(encoding="utf-8")

            if text.strip():
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source_file": source,
                            "page": "N/A",
                        },
                    )
                )

    return documents
