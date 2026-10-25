
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.storage.file_storage import (
    save_file,
    read_file,
    delete_file,
    file_exists,
)


def test_provider(provider: str) -> None:
    filename = f"storage-test-{uuid.uuid4().hex}.txt"
    content = b"Smart RFP Assistant storage abstraction test."

    print(f"\nTesting provider: {provider}")

    try:
        save_file(filename, content, provider)

        assert file_exists(filename, provider)
        print("Upload: PASS")

        downloaded = read_file(filename, provider)

        assert downloaded == content
        print("Read and integrity: PASS")

    finally:
        delete_file(filename, provider)

    assert not file_exists(filename, provider)
    print("Delete: PASS")


if __name__ == "__main__":
    test_provider("local")
    test_provider("azure_blob")

    print("\nALL STORAGE TESTS PASSED")
