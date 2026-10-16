


import re


CITATION_PATTERN = re.compile(r"\[Source (\d+)\]")


def validate_citations(
    answer: str,
    evidence: list[dict],
) -> tuple[bool, list[dict]]:
    """Validate citation indices and return cited sources."""

    cited_indices = {
        int(index)
        for index in CITATION_PATTERN.findall(answer)
    }

    if not cited_indices:
        return False, []

    valid_indices = set(range(1, len(evidence) + 1))

    if not cited_indices.issubset(valid_indices):
        return False, []

    cited_sources = []

    for index in sorted(cited_indices):
        item = evidence[index - 1]

        cited_sources.append({
            "source_file": item["source_file"],
            "page": item["page"],
            "chunk_id": item["chunk_id"],
        })

    return True, cited_sources
