import re


MARKDOWN_TABLE_ROW = re.compile(
    r"(?m)^\s*\|.+\|\s*$"
)

HTML_TABLE = re.compile(
    r"<table\b",
    re.IGNORECASE,
)

FIGURE_MARKER = re.compile(
    r"<figure\b",
    re.IGNORECASE,
)


def detect_content_type(text: str) -> str:
    """Classify visible Markdown/HTML layout markers.

    This is a lightweight heuristic, not a replacement for
    structured layout information from Document Intelligence.
    """

    has_table = bool(
        HTML_TABLE.search(text)
        or MARKDOWN_TABLE_ROW.search(text)
    )

    has_figure = bool(FIGURE_MARKER.search(text))

    if has_table and has_figure:
        return "mixed"

    if has_table:
        return "table"

    if has_figure:
        return "figure"

    return "text"