"""Tests for application settings."""

import pytest
from pydantic import ValidationError

from app.settings import Settings


class TestSettings:
    """Tests for Settings class."""

    def test_defaults(self) -> None:
        """Test default values when no env vars are set."""
        settings = Settings(
            _env_file=None,  # type: ignore[call-arg]
        )
        assert settings.environment == "dev"
        assert settings.agent_mode == "local"
        assert settings.agent_lambda_function_name == ""
        assert settings.aws_region == "us-east-2"

    def test_reads_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that settings reads from environment variables."""
        monkeypatch.setenv("ENVIRONMENT", "prod")
        monkeypatch.setenv("AGENT_MODE", "lambda")
        monkeypatch.setenv("AGENT_LAMBDA_FUNCTION_NAME", "my-agent")
        monkeypatch.setenv("AWS_REGION", "eu-west-1")

        settings = Settings(
            _env_file=None,  # type: ignore[call-arg]
        )
        assert settings.environment == "prod"
        assert settings.agent_mode == "lambda"
        assert settings.agent_lambda_function_name == "my-agent"
        assert settings.aws_region == "eu-west-1"

    def test_invalid_agent_mode_rejected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid AGENT_MODE values fail validation."""
        monkeypatch.setenv("AGENT_MODE", "invalid")

        with pytest.raises(ValidationError, match="agent_mode"):
            Settings(
                _env_file=None,  # type: ignore[call-arg]
            )
