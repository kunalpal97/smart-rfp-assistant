
from functools import lru_cache

from azure.storage.blob import BlobServiceClient

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_blob_service_client() -> BlobServiceClient:
    settings = get_settings()

    account_name = settings.azure_storage_account_name.strip()
    account_key = settings.azure_storage_account_key.strip()

    if not account_name or not account_key:
        raise ValueError(
            "Azure Blob Storage account name or key is missing."
        )

    account_url = (
        f"https://{account_name}.blob.core.windows.net"
    )

    return BlobServiceClient(
        account_url=account_url,
        credential=account_key,
    )


def get_document_container_client():
    settings = get_settings()

    container_name = settings.azure_storage_container_name.strip()

    if not container_name:
        raise ValueError(
            "Azure Blob Storage container name is missing."
        )

    return get_blob_service_client().get_container_client(
        container_name
    )
