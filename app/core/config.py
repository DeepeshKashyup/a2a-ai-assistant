""" Application configurations loader from environment variables and .env files. """

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central config - all values can be overridden via environment variables. """
    # -- App -----------------------------------------------------
    app_name: str = "A2A Content Assistant"
    app_version: str = "0.1.3"
    env: str = Field(default="development", alias ="APP_ENV")
    debug: bool = False

    # -- Server --------------------------------------------------
    host : str = "0.0.0.0"
    port: int = 8000
    cors_origins: List[str] = ["*"]  # Allow all origins for CORS

settings = Settings()