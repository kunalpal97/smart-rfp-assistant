def extract_structured_tables(result) -> list[dict]:
    """Convert Azure Document Intelligence tables to JSON-friendly data.

    Supports normal table cells and merged cells.
    Preserves source page numbers for citations.
    """
    extracted_tables = []

    for table_index, table in enumerate(
        result.tables or [], start=1
    ):
        # Create an empty matrix matching the detected table size.
        matrix = [
            [""] * table.column_count
            for _ in range(table.row_count)
        ]

        for cell in table.cells:
            row_span = cell.row_span or 1
            column_span = cell.column_span or 1

            if (
                cell.row_index < 0
                or cell.column_index < 0
                or cell.row_index + row_span > table.row_count
                or cell.column_index + column_span > table.column_count
            ):
                raise ValueError(
                    f"Invalid table cell coordinates in table {table_index}"
                )

            # Store actual text only in the cell's starting position.
            # Merged cells are represented separately in the metadata.
            matrix[cell.row_index][cell.column_index] = (
                cell.content or ""
            )

        pages = sorted({
            region.page_number
            for region in (table.bounding_regions or [])
        })

        # A header row is not guaranteed. Only use one if Azure
        # explicitly identifies header cells in the first row.
        has_header = any(
            cell.row_index == 0
            and cell.kind == "columnHeader"
            for cell in table.cells
        )

        columns = matrix[0] if has_header else []

        rows = matrix[1:] if has_header else matrix

        extracted_tables.append({
            "table_id": f"table-{table_index}",
            "content_type": "table",
            "pages": pages,
            "columns": columns,
            "rows": rows,
            "merged_cells": [
                {
                    "row": cell.row_index,
                    "column": cell.column_index,
                    "row_span": cell.row_span or 1,
                    "column_span": cell.column_span or 1,
                }
                for cell in table.cells
                if (cell.row_span or 1) > 1
                or (cell.column_span or 1) > 1
            ],
        })

    return extracted_tables


def extract_structured_figures(result) -> list[dict]:
    """Convert Azure figure metadata into JSON-friendly records.

    Preserve figure IDs, captions and page references.
    Does not download or generate figure images.
    """
    figures = []

    for index, figure in enumerate(
        result.figures or [], start=1
    ):
        pages = sorted({
            region.page_number
            for region in (figure.bounding_regions or [])
        })

        caption = (
            figure.caption.content.strip()
            if figure.caption and figure.caption.content
            else None
        )

        figures.append({
            "figure_id": figure.id or f"figure-{index}",
            "content_type": "figure",
            "pages": pages,
            "caption": caption,
        })

    return figures


def summarize_structured_content(result) -> dict:
    """Return structured layout metadata without modifying extracted pages.

    Useful for inspection and later indexing integration.
    """
    tables = extract_structured_tables(result)
    figures = extract_structured_figures(result)

    return {
        "tables": tables,
        "figures": figures,
        "table_count": len(tables),
        "figure_count": len(figures),
    }