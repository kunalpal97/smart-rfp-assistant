
from pathlib import Path
from typing import Literal

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import ContentSettings

from app.core.config import get_settings
from app.integrations.azure_blob import get_document_container_client


StorageProvider = Literal["local", "azure_blob"]


def get_storage_provider() -> StorageProvider:
    """Return the configured storage provider."""

    provider = get_settings().file_storage_provider.strip().lower()

    if provider not in {"local", "azure_blob"}:
        raise ValueError(
            f"Unsupported FILE_STORAGE_PROVIDER: {provider}"
        )

    return provider


def _validate_filename(stored_filename: str) -> str:
    """Prevent directory traversal and invalid stored filenames."""

    if (
        not stored_filename
        or stored_filename in {".", ".."}
        or Path(stored_filename).name != stored_filename
        or "\\" in stored_filename
        or "/" in stored_filename
    ):
        raise ValueError("Invalid stored filename.")

    return stored_filename


def save_file(
    stored_filename: str,
    content: bytes,
    provider: StorageProvider,
) -> None:
    """Save original document to local disk or Azure Blob."""

    stored_filename = _validate_filename(stored_filename)

    if provider == "local":
        upload_dir = get_settings().upload_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        path = upload_dir / stored_filename
        with path.open("xb") as file:
            file.write(content)

    elif provider == "azure_blob":
        container = get_document_container_client()

        blob = container.get_blob_client(
            f"documents/{stored_filename}"
        )

        blob.upload_blob(
            content,
            overwrite=False,
            content_settings=ContentSettings(
                content_type="application/octet-stream"
            ),
        )

    else:
        raise ValueError(f"Unsupported storage provider: {provider}")


def read_file(
    stored_filename: str,
    provider: StorageProvider,
) -> bytes:
    """Read original document from its recorded storage provider."""

    stored_filename = _validate_filename(stored_filename)

    if provider == "local":
        path = get_settings().upload_dir / stored_filename
        return path.read_bytes()

    if provider == "azure_blob":
        blob = get_document_container_client().get_blob_client(
            f"documents/{stored_filename}"
        )

        return blob.download_blob().readall()

    raise ValueError(f"Unsupported storage provider: {provider}")


def delete_file(
    stored_filename: str,
    provider: StorageProvider,
) -> None:
    """Delete original document from the correct storage provider."""

    stored_filename = _validate_filename(stored_filename)

    if provider == "local":
        path = get_settings().upload_dir / stored_filename
        path.unlink(missing_ok=True)
        return

    if provider == "azure_blob":
        blob = get_document_container_client().get_blob_client(
            f"documents/{stored_filename}"
        )

        try:
            blob.delete_blob()
        except ResourceNotFoundError:
            # Idempotent deletion: already deleted is acceptable.
            pass

        return

    raise ValueError(f"Unsupported storage provider: {provider}")


def file_exists(
    stored_filename: str,
    provider: StorageProvider,
) -> bool:
    """Check whether the original file exists."""

    stored_filename = _validate_filename(stored_filename)

    if provider == "local":
        return (
            get_settings().upload_dir / stored_filename
        ).is_file()

    if provider == "azure_blob":
        blob = get_document_container_client().get_blob_client(
            f"documents/{stored_filename}"
        )
        return blob.exists()

    raise ValueError(f"Unsupported storage provider: {provider}")
