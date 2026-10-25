
import re


CITATION_PATTERN = re.compile(
    r"\[Source\s+(\d+(?:\s*,\s*Source\s+\d+)*)\]"
)


def validate_citations(
    answer: str,
    evidence: list[dict],
) -> tuple[bool, list[dict]]:
    """Validate citations and preserve source metadata."""

    citation_groups = CITATION_PATTERN.findall(answer)

    if not citation_groups:
        return False, []

    cited_indices = set()

    for group in citation_groups:
        indices = re.findall(
            r"Source\s+(\d+)",
            f"Source {group}",
        )

        for index in indices:
            cited_indices.add(int(index))

    valid_indices = set(range(1, len(evidence) + 1))

    if not cited_indices.issubset(valid_indices):
        return False, []

    cited_sources = []

    for index in sorted(cited_indices):
        item = evidence[index - 1]

        
        cited_sources.append({
            "source_id": f"Source {index}",
            "source_file": item["source_file"],
            "page": item["page"],
            "chunk_id": item["chunk_id"],
            "evidence": item["text"],
            "distance": item.get("distance"),

            # Preserve metadata from retrieval
            "document_id": item.get("document_id"),
            "content_type": item.get("content_type", "text"),
            "table_ids": item.get("table_ids") or [],
            "figure_ids": item.get("figure_ids") or [],

            # Populated only after PostgreSQL enrichment
            "structured_elements": item.get("structured_elements") or [],
        })


    return True, cited_sources
