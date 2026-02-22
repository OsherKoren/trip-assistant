"""Application settings via pydantic-settings.

Reads from environment variables at startup (no env prefix).
Validates configuration early — invalid AGENT_MODE fails fast.
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
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings (created once, reused)."""
    return Settings()
