
from app.services.rag import get_evidence
from app.services.evidence_assessment import assess_evidence


questions = [
    "What are the P1 and P2 response and resolution times?",
    "Does NovaTech provide quantum computing infrastructure with a guaranteed 99.999% SLA?",
]

for question in questions:
    print("\nQuestion:", question)

    evidence = get_evidence(
        question=question,
        retrieval_mode="hybrid",
        top_k=3,
    )

    result = assess_evidence(
        question=question,
        evidence=evidence,
    )

    print("Status:", result.status)
    print("Reason:", result.reason)
