

import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


def get_llm() -> ChatGroq:
    """Create a Groq chat model client."""

    api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    )

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from the .env file."
        )

    return ChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=0,
        max_retries=2,
    )
