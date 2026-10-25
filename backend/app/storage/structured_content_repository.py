
"""Persistence for extracted PDF tables and figures."""

from sqlalchemy import delete, select

from app.storage.db_engine import get_db_session
from app.storage.models import Document, DocumentElement


def save_document_elements(
    document_id: str,
    structured: dict,
) -> int:
    """Replace a document's structured elements atomically.

    The parent document must already exist.
    If insertion fails, the transaction is rolled back.
    """
    tables = structured.get("tables", [])
    figures = structured.get("figures", [])

    if not isinstance(tables, list) or not isinstance(figures, list):
        raise ValueError("Tables and figures must be lists.")

    records = []

    for table in tables:
        pages = table.get("pages") or []

        if not pages:
            raise ValueError("Table is missing page information.")

        records.append({
            "element_id": table["table_id"],
            "element_type": "table",
            "page_number": min(pages),
            "content_json": table,
        })

    for figure in figures:
        pages = figure.get("pages") or []

        if not pages:
            raise ValueError("Figure is missing page information.")

        records.append({
            "element_id": figure["figure_id"],
            "element_type": "figure",
            "page_number": min(pages),
            "content_json": figure,
        })

    # Validate uniqueness before touching existing records.
    identities = [
        (item["element_type"], item["element_id"])
        for item in records
    ]

    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate structured element IDs detected.")

    with get_db_session() as session:
        parent = session.get(Document, document_id)

        if parent is None:
            raise ValueError(
                f"Document not found: {document_id}"
            )

        # Replacing records makes repeated ingestion idempotent.
        # Delete and insert occur in the same transaction.
        session.execute(
            delete(DocumentElement).where(
                DocumentElement.document_id == document_id
            )
        )

        for record in records:
            session.add(
                DocumentElement(
                    document_id=document_id,
                    **record,
                )
            )

        session.flush()

    return len(records)


def get_document_elements(
    document_id: str,
    element_type: str | None = None,
) -> list[dict]:
    """Retrieve structured elements belonging to a document."""
    if element_type not in (None, "table", "figure"):
        raise ValueError(
            "element_type must be 'table', 'figure', or None."
        )

    with get_db_session() as session:
        statement = select(DocumentElement).where(
            DocumentElement.document_id == document_id
        )

        if element_type is not None:
            statement = statement.where(
                DocumentElement.element_type == element_type
            )

        statement = statement.order_by(
            DocumentElement.page_number,
            DocumentElement.id,
        )

        elements = session.scalars(statement).all()

        return [
            {
                "id": element.id,
                "document_id": element.document_id,
                "element_id": element.element_id,
                "element_type": element.element_type,
                "page_number": element.page_number,
                "content": element.content_json,
            }
            for element in elements
        ]


def delete_document_elements(document_id: str) -> int:
    """Delete structured elements for a document."""

    with get_db_session() as session:
        result = session.execute(
            delete(DocumentElement).where(
                DocumentElement.document_id == document_id
            )
        )

        return result.rowcount