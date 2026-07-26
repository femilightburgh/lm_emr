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

    secret_key: str

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    refresh_token_expire_days: int = 7

    max_failed_login_attempts: int = 5

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