
from app.services.retrieval import retrieve_evidence
from app.services.keyword_retrieval import retrieve_keyword_evidence
from app.services.hybrid_retrieval import retrieve_hybrid_evidence


TEST_CASES = [
    {
        "question": (
            "What are the P1 and P2 response "
            "and resolution times?"
        ),
        "source": "Proposal_Governance_Delivery_2024.md",
        "required_text": "Resolution Time",
    },
    {
        "question": "What is your cloud migration approach?",
        "source": "Proposal_CloudMigration_FinServe_2024.pdf",
        "required_text": "Assessment",
    },
    {
        "question": (
            "How do you manage project governance "
            "and reporting?"
        ),
        "source": "Proposal_Governance_Delivery_2024.md",
        "required_text": "Steering Committee",
    },
    {
        "question": (
            "What are your disaster recovery "
            "RTO and RPO commitments?"
        ),
        "source": "Proposal_Security_Compliance_2024.txt",
        "required_text": "Recovery Time Objective",
    },
]


METHODS = {
    "Semantic": lambda q: retrieve_evidence(q, top_k=5),
    "BM25": lambda q: retrieve_keyword_evidence(q, top_k=5),
    "Hybrid": lambda q: retrieve_hybrid_evidence(
        q,
        top_k=5,
        candidate_k=10,
    ),
}


def find_relevant_rank(results, case):
    for rank, item in enumerate(results, start=1):
        if (
            item["source_file"] == case["source"]
            and case["required_text"].lower()
            in item["text"].lower()
        ):
            return rank

    return None


def main():
    for method_name, search in METHODS.items():
        print("\n" + "=" * 60)
        print("METHOD:", method_name)

        top_1_hits = 0
        top_5_hits = 0
        reciprocal_ranks = []

        for case in TEST_CASES:
            results = search(case["question"])
            rank = find_relevant_rank(results, case)

            if rank == 1:
                top_1_hits += 1

            if rank is not None:
                top_5_hits += 1

            reciprocal_ranks.append(
                1 / rank if rank is not None else 0
            )

            print(
                f"\nQuestion: {case['question']}"
                f"\nRelevant chunk rank: {rank}"
            )

        total = len(TEST_CASES)

        print(f"\nChunk Hit@1: {top_1_hits / total:.1%}")
        print(f"Chunk Hit@5: {top_5_hits / total:.1%}")
        print(
            "Chunk MRR@5:",
            round(sum(reciprocal_ranks) / total, 3),
        )


if __name__ == "__main__":
    main()
