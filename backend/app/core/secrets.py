"""
Utility to load secrets from AWS Secrets Manager into environment variables.
This is optional and only used when `USE_AWS_SECRETS` is truthy.

Usage: set environment variables `USE_AWS_SECRETS=1` and `AWS_SECRET_NAME`.
"""
from __future__ import annotations

import os
import json
import logging

logger = logging.getLogger(__name__)


def load_aws_secrets_to_env(secret_name: str) -> None:
    try:
        import boto3
        from botocore.exceptions import BotoCoreError, ClientError
    except Exception:
        logger.exception("boto3 not available; cannot load AWS secrets")
        return

    if not secret_name:
        logger.warning("No AWS secret name provided; skipping secrets load")
        return

    try:
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=secret_name)
        secret = resp.get("SecretString")
        if not secret:
            logger.warning("Empty secret string for %s", secret_name)
            return

        data = json.loads(secret)
        if not isinstance(data, dict):
            logger.warning("Secrets payload is not a JSON object")
            return

        for k, v in data.items():
            if k in os.environ:
                # don't overwrite explicit env vars
                continue
            os.environ[k] = str(v)
        logger.info("Loaded %d secrets into environment from %s", len(data), secret_name)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Failed to load secret %s: %s", secret_name, exc)
    except Exception:
        logger.exception("Unexpected error loading AWS secrets")
