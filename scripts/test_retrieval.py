
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.retrieval import (
    retrieve_evidence,
    retrieve_relevant_evidence,
)


EVALUATION_FILE = (
    PROJECT_ROOT / "data" / "evaluation" / "rfp_questions.json"
)

TOP_K = 3



def evaluate_retrieval():
    """Evaluate positive retrieval and negative rejection cases."""

    with EVALUATION_FILE.open(encoding="utf-8") as file:
        questions = json.load(file)

    if not questions:
        print("No evaluation questions found.")
        return

    positive_count = 0
    negative_count = 0
    raw_hits = 0
    filtered_hits = 0
    reciprocal_rank_sum = 0.0
    false_positives = 0

    for item in questions:
        question = item["question"]
        expected_sources = set(item["expected_sources"])

        raw_results = retrieve_evidence(question, top_k=TOP_K)
        filtered_results = retrieve_relevant_evidence(
            question, top_k=TOP_K
        )

        raw_sources = [
            result["source_file"] for result in raw_results
        ]
        filtered_sources = [
            result["source_file"] for result in filtered_results
        ]

        print(f"\n{item['id']}: {question}")
        print(f"Expected: {sorted(expected_sources)}")
        print(f"Raw sources: {raw_sources}")
        print(f"Filtered sources: {filtered_sources}")

        if not expected_sources:
            negative_count += 1

            if filtered_results:
                false_positives += 1
                print("Result: FALSE POSITIVE")
            else:
                print("Result: CORRECT REJECTION")

            continue

        positive_count += 1

        if expected_sources.intersection(raw_sources):
            raw_hits += 1

        if expected_sources.intersection(filtered_sources):
            filtered_hits += 1

        reciprocal_rank = 0.0

        for rank, source in enumerate(filtered_sources, start=1):
            if source in expected_sources:
                reciprocal_rank = 1 / rank
                break

        reciprocal_rank_sum += reciprocal_rank

        print(f"Reciprocal rank: {reciprocal_rank:.3f}")

    print("\n" + "=" * 55)
    print("RETRIEVAL EVALUATION SUMMARY")
    print("=" * 55)

    print(f"Positive questions: {positive_count}")
    print(f"Negative questions: {negative_count}")

    if positive_count:
        print(
            f"Raw Hit Rate@{TOP_K}: "
            f"{raw_hits / positive_count:.2%}"
        )
        print(
            f"Filtered Hit Rate@{TOP_K}: "
            f"{filtered_hits / positive_count:.2%}"
        )
        print(
            f"Filtered MRR@{TOP_K}: "
            f"{reciprocal_rank_sum / positive_count:.3f}"
        )

    if negative_count:
        print(
            "False Positive Rate: "
            f"{false_positives / negative_count:.2%}"
        )
        print(
            "Correct Rejection Rate: "
            f"{(negative_count - false_positives) / negative_count:.2%}"
        )


if __name__ == "__main__":
    evaluate_retrieval()
