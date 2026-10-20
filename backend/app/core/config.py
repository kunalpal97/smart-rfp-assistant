

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

    # Groq configuration
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

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
