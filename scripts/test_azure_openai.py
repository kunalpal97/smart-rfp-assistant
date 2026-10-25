
"""Test Azure OpenAI using the Responses API."""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, APIStatusError

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "").strip()

if not endpoint or not api_key or not deployment:
    raise ValueError("Azure OpenAI configuration is incomplete.")

# Base URL only; SDK adds /responses automatically.
client = OpenAI(
    base_url=f"{endpoint}/openai/v1/",
    api_key=api_key,
    timeout=30.0,
    max_retries=1,
)

try:
    response = client.responses.create(
        model=deployment,
        instructions="You are a helpful enterprise RFP assistant.",
        input="Explain what an RFP is in two sentences.",
        max_output_tokens=150,
    )

    print("Deployment:", deployment)
    print("Response:", response.output_text)

    if response.usage:
        print("Input tokens:", response.usage.input_tokens)
        print("Output tokens:", response.usage.output_tokens)

except APIStatusError as exc:
    print("Azure API status:", exc.status_code)
    print("Azure API error:", exc.message)
    raise
