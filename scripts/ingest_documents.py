
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))

from app.services.ingestion import load_documents
from app.utils.chunking import chunk_documents
from app.storage.vector_store import store_chunks, get_collection


def main():
    documents_path = PROJECT_ROOT / "data" / "mock_proposals"

    print("Loading documents...")
    documents = load_documents(documents_path)

    print("Creating chunks...")
    chunks = chunk_documents(documents)

    print("Storing embeddings in ChromaDB...")
    stored = store_chunks(chunks)

    print(f"Documents/pages loaded: {len(documents)}")
    print(f"Chunks processed: {stored}")
    print(f"Total ChromaDB records: {get_collection().count()}")


if __name__ == "__main__":
    main()
