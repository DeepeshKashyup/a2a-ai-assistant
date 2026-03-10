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
    app_version: str = "0.1.4"
    env: str = Field(default="development", alias ="APP_ENV")
    debug: bool = False

    # -- Server --------------------------------------------------
    host : str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]  # Allow all origins for CORS

    # -- GCP & LLM --------------------------------------------------
    gcp_project_id: str = Field(..., env="GCP_PROJECT_ID")
    gcp_location: str = Field('us-central1', env="GCP_LOCATION")
    llm_model : str = Field('gemini-1.5-flash-001', env="LLM_MODEL")
    llm_temperature: float = Field(0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(2048, env="LLM_MAX_TOKENS")

settings = Settings()