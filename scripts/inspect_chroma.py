
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.storage.vector_store import get_collection # type: ignore


def main():
    collection = get_collection()

    print(f"Total records: {collection.count()}")

    results = collection.get(
        include=["metadatas"]
    )

    for record_id, metadata in zip(
        results["ids"],
        results["metadatas"],
    ):
        print("\nRecord ID:", record_id)
        print("Metadata:", metadata)


if __name__ == "__main__":
    main()
