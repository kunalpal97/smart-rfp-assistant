

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Central application configuration."""

    # Provider selection
    llm_provider: str = "groq"
    embedding_provider: str = "local"
    document_extractor: str = "pypdf"
    file_storage_provider: str = "local"
    vector_store_provider: str = "chroma"

    # Optional Azure AI Search indexing during migration
    azure_search_enabled: bool = False

    # Groq configuration
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    # Azure OpenAI configuration
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_chat_deployment: str = ""
    azure_openai_embedding_deployment: str = ""

    # Microsoft Entra ID authentication
    entra_tenant_id: str = ""
    entra_client_id: str = ""
    entra_api_audience: str = ""
    entra_required_scope: str = "access_as_user"

    # Azure Document Intelligence configuration
    azure_document_intelligence_endpoint: str = ""
    azure_document_intelligence_key: str = ""


    # Azure Blob Storage
    azure_storage_account_name: str = ""
    azure_storage_container_name: str = "rfp-documents"
    azure_storage_account_key: str = ""

    # Database configuration
    database_provider: str = "sqlite"
    database_url: str = ""

    # Local embedding configuration
    local_embedding_model: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # Application paths
    upload_dir: Path = PROJECT_ROOT / "data" / "uploads"
    chroma_dir: Path = PROJECT_ROOT / "storage" / "chroma"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Read configuration once and reuse it."""
    return Settings()
