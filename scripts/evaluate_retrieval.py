
from app.services.retrieval import retrieve_evidence
from app.services.keyword_retrieval import retrieve_keyword_evidence
from app.services.hybrid_retrieval import retrieve_hybrid_evidence


TEST_CASES = [
    {
        "question": "What are the P1 and P2 response and resolution times?",
        "expected": "Proposal_Governance_Delivery_2024.md",
    },
    {
        "question": "What is your cloud migration approach?",
        "expected": "Proposal_CloudMigration_FinServe_2024.pdf",
    },
    {
        "question": "What encryption and security controls do you provide?",
        "expected": "Proposal_Security_Compliance_2024.txt",
    },
    {
        "question": "How do you manage project governance and reporting?",
        "expected": "Proposal_Governance_Delivery_2024.md",
    },
    {
        "question": "What are your disaster recovery RTO and RPO commitments?",
        "expected": "Proposal_Security_Compliance_2024.txt",
    },

    {
        "question": (
            "How quickly can you restore critical systems "
            "after an unexpected outage?"
        ),
        "expected": "Proposal_Security_Compliance_2024.txt",
    },
    {
        "question": (
            "How do you move business applications to a "
            "new cloud environment while minimizing disruption?"
        ),
        "expected": "Proposal_CloudMigration_FinServe_2024.pdf",
    },
    {
        "question": (
            "How do you keep customers informed about "
            "project progress and major risks?"
        ),
        "expected": "Proposal_Governance_Delivery_2024.md",
    },
    {
        "question": (
            "How do you protect sensitive customer "
            "information while it is stored and transmitted?"
        ),
        "expected": "Proposal_Security_Compliance_2024.txt",
    },
    {
        "question": (
            "When a business-critical application stops working, "
            "how soon will your support team respond and fix it?"
        ),
        "expected": "Proposal_Governance_Delivery_2024.md",
    },

]


METHODS = {
    "Semantic": lambda q: retrieve_evidence(q, top_k=5),
    "BM25": lambda q: retrieve_keyword_evidence(q, top_k=5),
    "Hybrid": lambda q: retrieve_hybrid_evidence(
        q, top_k=5, candidate_k=10
    ),
}


def main():
    for method_name, search in METHODS.items():
        print(f"\n{'=' * 60}")
        print("METHOD:", method_name)

        reciprocal_ranks = []
        top_1_hits = 0

        for case in TEST_CASES:
            results = search(case["question"])

            rank = next(
                (
                    index
                    for index, item in enumerate(results, start=1)
                    if item["source_file"] == case["expected"]
                ),
                None,
            )

            reciprocal_ranks.append(
                1 / rank if rank is not None else 0
            )

            if rank == 1:
                top_1_hits += 1

            print(
                f"\nQuestion: {case['question']}"
                f"\nExpected document rank: {rank}"
            )

        total = len(TEST_CASES)
        mrr = sum(reciprocal_ranks) / total

        print(f"\nTop-1 accuracy: {top_1_hits / total:.1%}")
        print(f"MRR@5: {mrr:.3f}")


if __name__ == "__main__":
    main()
