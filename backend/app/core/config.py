"""
========================================================================

LIGHTBURGH EMR

Application Configuration

========================================================================

Purpose
-------

This module centralizes all application configuration.

Configuration values are loaded from environment variables and exposed
through a strongly typed Settings object.

No other part of the application should access environment variables
directly.

========================================================================
"""

import os
import re
import logging

from dotenv import dotenv_values
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Optionally load secrets from AWS Secrets Manager early so Settings can pick them up
if os.environ.get("USE_AWS_SECRETS"):
    try:
        from app.core.secrets import load_aws_secrets_to_env

        secret_name = os.environ.get("AWS_SECRET_NAME")
        logging.getLogger(__name__).info("Loading secrets from AWS Secrets Manager: %s", secret_name)
        load_aws_secrets_to_env(secret_name)
    except Exception:
        logging.getLogger(__name__).exception("Failed to load AWS secrets")


class Settings(BaseSettings):
    """
    Global application settings.

    Every attribute defined here maps to an environment variable
    in the project's `.env` file.
    """

    # ----------------------------------------------------------
    # Application
    # ----------------------------------------------------------

    app_name: str = "LIGHTBURGH EMR"

    api_version: str = "v1"

    app_env: str = "development"

    debug: bool = True

    allowed_origins: str = Field(
        default="http://localhost:5173,http://localhost:5174,https://localhost:5173,https://localhost:5174",
        validation_alias="ALLOWED_ORIGINS",
    )

    @field_validator("debug", mode="before")
    @classmethod
    def set_debug_from_app_env(cls, value, info):
        app_env = info.data.get("app_env") if info.data else None
        if app_env is not None and app_env.lower() == "production":
            return False
        if app_env is not None and app_env.lower() in {"development", "staging"}:
            return True
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value, info):
        app_env = info.data.get("app_env") if info.data else None
        if app_env and app_env.lower() == "production" and len(value) < 32:
            raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters long in production."
            )
        return value

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    database_url: str

    # ----------------------------------------------------------
    # Storage
    # ----------------------------------------------------------

    storage_backend: str = "local"

    storage_path: str = "./storage"

    storage_max_file_size_mb: int = 20

    storage_allowed_content_types: str = (
        "application/pdf,image/jpeg,image/png"
    )

    # ----------------------------------------------------------
    # Security
    # ----------------------------------------------------------

    jwt_secret_key: str = Field(
        validation_alias="JWT_SECRET_KEY"
    )

    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias="JWT_ALGORITHM",
    )

    access_token_expire_minutes: int = Field(
        default=15,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    refresh_token_expire_days: int = Field(
        default=30,
        validation_alias="REFRESH_TOKEN_EXPIRE_DAYS",
    )

    max_failed_login_attempts: int = Field(
        default=5,
        validation_alias="MAX_FAILED_LOGIN_ATTEMPTS",
    )

    # ----------------------------------------------------------
    # Pydantic Settings Configuration
    # ----------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url", mode="before")
    @classmethod
    def expand_database_url(cls, value):
        """Expand environment-style variables in the database URL.

        Supports $VAR, ${VAR} and {VAR} placeholder formats. This makes
        it convenient to use templates in `.env` like
        `postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}`.
        """

        if not value or not isinstance(value, str):
            return value

        # expand $VAR and ${VAR}
        expanded = os.path.expandvars(value)

        # Pydantic reads .env values for Settings, but does not add them to
        # os.environ. Load that file here too so a DATABASE_URL template can
        # reliably reference POSTGRES_* values declared alongside it.
        env_file_values = dotenv_values(".env")

        # replace {VAR} with environment or .env value if present
        def _repl(match):
            name = match.group(1)
            return (
                os.environ.get(name)
                or env_file_values.get(name)
                or match.group(0)
            )

        expanded = re.sub(r"\{([A-Za-z0-9_]+)\}", _repl, expanded)

        return expanded


# Singleton settings instance
settings = Settings()
