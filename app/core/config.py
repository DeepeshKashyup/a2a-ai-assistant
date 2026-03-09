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
    app_version: str = "0.1.0"
    env: str = Field(default="development", alias ="APP_ENV")
    debug: bool = False

    # -- Server --------------------------------------------------
    host : str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]  # Allow all origins for CORS

settings = Settings()