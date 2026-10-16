
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.integrations.groq_client import get_llm


def main():
    llm = get_llm()

    response = llm.invoke(
        "Reply with exactly: Groq connection successful"
    )

    print("Model response:", response.content)


if __name__ == "__main__":
    main()
