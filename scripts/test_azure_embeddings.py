
"""Test Azure text-embedding-3-large independently."""

import os
import math
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env", override=True)

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/")
api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
deployment = os.getenv(
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", ""
).strip()

if not all([endpoint, api_key, deployment]):
    raise ValueError("Azure embedding configuration is incomplete.")

client = OpenAI(
    base_url=f"{endpoint}/openai/v1/",
    api_key=api_key,
    timeout=60.0,
    max_retries=1,
)

texts = [
    "The company provides 24/7 technical support.",
    "Technical assistance is available around the clock.",
    "The company provides catering services for events.",
]

response = client.embeddings.create(
    model=deployment,
    input=texts,
)

vectors = [
    item.embedding
    for item in sorted(response.data, key=lambda x: x.index)
]

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)

print("Embedding deployment:", deployment)
print("Number of vectors:", len(vectors))
print("Vector dimensions:", len(vectors[0]))

print(
    "Similar sentences:",
    round(cosine_similarity(vectors[0], vectors[1]), 4),
)

print(
    "Unrelated sentences:",
    round(cosine_similarity(vectors[0], vectors[2]), 4),
)

if response.usage:
    print("Total tokens:", response.usage.total_tokens)
