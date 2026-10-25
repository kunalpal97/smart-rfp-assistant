import re
from html import unescape


FIGURE_OPEN = re.compile(r"<figure\b[^>]*>", re.IGNORECASE)
FIGURE_CLOSE = re.compile(r"</figure\s*>", re.IGNORECASE)

FIGCAPTION_OPEN = re.compile(
    r"<figcaption\b[^>]*>", re.IGNORECASE
)
FIGCAPTION_CLOSE = re.compile(
    r"</figcaption\s*>", re.IGNORECASE
)


def normalize_content(text: str) -> str:
    """Make extracted figure markup readable without losing content.

    This intentionally handles figure-related tags only.
    Tables and other HTML structures are preserved for later processing.
    """
    if not text:
        return ""

    normalized = unescape(text)

    # Preserve figure contents and captions as readable text.
    normalized = FIGURE_OPEN.sub("\n\n", normalized)
    normalized = FIGURE_CLOSE.sub("\n\n", normalized)
    normalized = FIGCAPTION_OPEN.sub("\nCaption: ", normalized)
    normalized = FIGCAPTION_CLOSE.sub("\n", normalized)

    # Normalize excessive blank lines without collapsing table rows.
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()