
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.services.rag import answer_rfp_question


QUESTIONS = [
    "How does your company protect customer data?",
    "What is your approach to cloud migration?",
    "Is your company ISO 27001 certified?",
    "Does your company provide employee health insurance?",
]


def main():
    for question in QUESTIONS:
        print(f"\n{'=' * 60}")
        print(f"QUESTION: {question}")

        result = answer_rfp_question(question)

        print(f"\nANSWER:\n{result['answer']}")
        print(f"\nSOURCES:\n{result['sources']}")


if __name__ == "__main__":
    main()
