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

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    database_url: str

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


# Singleton settings instance
settings = Settings()