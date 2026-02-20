"""Application settings via pydantic-settings.

Reads from environment variables at startup (no env prefix).
Validates configuration early — typos in AGENT_MODE fail fast.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration validated at startup."""

    environment: str = "dev"
    agent_mode: Literal["local", "lambda"] = "local"
    agent_lambda_function_name: str = ""
    aws_region: str = "us-east-2"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings (created once, reused)."""
    return Settings()
