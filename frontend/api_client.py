
import os

import requests


API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)


def ask_question(question: str) -> dict:
    response = requests.post(
        f"{API_BASE_URL}/api/questions/ask",
        json={"question": question},
        timeout=120,
    )

    response.raise_for_status()
    return response.json()
