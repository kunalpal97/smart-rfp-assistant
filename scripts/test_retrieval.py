
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.retrieval import (
    retrieve_evidence,
    retrieve_relevant_evidence,
    NO_EVIDENCE_MESSAGE,
)


QUESTIONS = [
    "How is customer data protected?",
    "What steps are involved in cloud migration?",
    "Does the company provide employee health insurance?",
    "Narendra Modi is the Prime Minister of which country?",
]


def main():
    for question in QUESTIONS:
        print(f"\nQUESTION: {question}")

        raw_evidence = retrieve_evidence(question, top_k=2)
        relevant_evidence = retrieve_relevant_evidence(
            question,
            top_k=2,
        )

        print(f"Raw results: {len(raw_evidence)}")
        print(f"After filtering: {len(relevant_evidence)}")

        if not relevant_evidence:
            print(f"Answer: {NO_EVIDENCE_MESSAGE}")
            continue

        for index, item in enumerate(relevant_evidence, start=1):
            print(f"\n  Evidence {index}")
            print(f"  Source: {item['source_file']}")
            print(f"  Distance: {item['distance']}")
            print(f"  Text: {item['text'][:150]}...")


if __name__ == "__main__":
    main()
