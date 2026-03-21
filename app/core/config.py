""" Application configurations loader from environment variables and .env files. """

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", env_file_encoding="utf-8")
    """Central config - all values can be overridden via environment variables. """
    # -- App -----------------------------------------------------
    app_name: str = "A2A Content Assistant"
    app_version: str = "0.1.8"
    env: str = Field(default="development", alias ="APP_ENV")
    debug: bool = False

    # -- Server --------------------------------------------------
    host : str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]  # Allow all origins for CORS

    # -- Chunking ------------------------------------------------
    chunk_size: int = Field(1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(200, alias="CHUNK_OVERLAP")

    # -- embedding ------------------------------------------------
    embedding_model: str = Field('text-embedding-004', alias="EMBEDDING_MODEL")

    # -- vector store ------------------------------------------------
    chroma_persistend_dir : str = Field("data/embeddings", alias="CHROMA_PERSISTENT_DIR")
    chroma_collection: str = Field("content_search", alias="CHROMA_COLLECTION")
    vector_search_top_k: int = Field(5, alias="VECTOR_SEARCH_TOP_K")

    # -- GCP & LLM --------------------------------------------------
    gcp_project_id: str = Field(...)
    gcp_location: str = Field('us-central1')
    llm_model: str = Field('gemini-2.0-flash-001')
    llm_temperature: float = Field(0.7)
    llm_max_tokens: int = Field(2048)

settings = Settings()