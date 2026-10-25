
import hashlib
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.integrations.azure_blob import get_document_container_client


def main():
    container = get_document_container_client()

    blob_name = f"connection-tests/{uuid.uuid4().hex}.txt"

    original_content = (
        b"Smart RFP Assistant - Azure Blob Storage integration test."
    )

    blob = container.get_blob_client(blob_name)

    uploaded = False

    try:
        print("1. Uploading test blob...")

        blob.upload_blob(
            original_content,
            overwrite=False,
        )
        uploaded = True

        print("   Upload: SUCCESS")

        print("2. Downloading test blob...")

        downloaded_content = blob.download_blob().readall()

        original_hash = hashlib.sha256(
            original_content
        ).hexdigest()

        downloaded_hash = hashlib.sha256(
            downloaded_content
        ).hexdigest()

        if original_hash != downloaded_hash:
            raise RuntimeError(
                "Downloaded content does not match uploaded content."
            )

        print("   Download: SUCCESS")
        print("   Integrity: PASS")

    finally:
        if uploaded:
            print("3. Deleting test blob...")

            blob.delete_blob()

            if blob.exists():
                raise RuntimeError(
                    "Test blob still exists after deletion."
                )

            print("   Delete: SUCCESS")

    print("\nAZURE BLOB STORAGE TEST: PASS")


if __name__ == "__main__":
    main()
