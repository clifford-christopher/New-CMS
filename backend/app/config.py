"""
Application Configuration

Centralized configuration management for:
- Environment variables
- API keys (local dev + AWS Secrets Manager)
- Database settings
- LLM provider configuration
"""

import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration"""

    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "mmfrontend")

    # FastAPI Configuration
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "News CMS API")

    # LLM Configuration
    LLM_TIMEOUT: float = float(os.getenv("LLM_TIMEOUT", "30.0"))
    LLM_MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "3"))
    LLM_DEFAULT_TEMPERATURE: float = float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.7"))
    LLM_DEFAULT_MAX_TOKENS: int = int(os.getenv("LLM_DEFAULT_MAX_TOKENS", "500"))

    # AWS Configuration
    USE_AWS_SECRETS: bool = os.getenv("USE_AWS_SECRETS", "false").lower() == "true"
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_SECRETS_MANAGER_PREFIX: str = os.getenv("AWS_SECRETS_MANAGER_PREFIX", "news-cms/")


def get_llm_api_keys() -> Dict[str, Optional[str]]:
    """
    Get LLM API keys from environment variables or AWS Secrets Manager

    In production (USE_AWS_SECRETS=true), keys are loaded from AWS Secrets Manager.
    In development, keys are loaded from environment variables.

    Returns:
        Dict with keys: openai, anthropic, google
    """
    if Config.USE_AWS_SECRETS:
        return _get_keys_from_aws_secrets()
    else:
        return _get_keys_from_env()


def _get_keys_from_env() -> Dict[str, Optional[str]]:
    """
    Get API keys from environment variables (local development)

    Returns:
        Dict with API keys
    """
    keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "gemini": os.getenv("GOOGLE_API_KEY"),
    }

    # Log which keys are available (without revealing the keys)
    for provider, key in keys.items():
        if key:
            logger.info(f"{provider.upper()} API key loaded from environment (length: {len(key)})")
        else:
            logger.warning(f"{provider.upper()} API key not found in environment")

    return keys


def _get_keys_from_aws_secrets() -> Dict[str, Optional[str]]:
    """
    Get API keys from AWS Secrets Manager (production)

    Returns:
        Dict with API keys

    Raises:
        Exception: If AWS Secrets Manager access fails
    """
    try:
        import boto3
        from botocore.exceptions import ClientError

        # Initialize AWS Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=Config.AWS_REGION
        )

        prefix = Config.AWS_SECRETS_MANAGER_PREFIX

        # Define secret names
        secret_names = {
            "openai": f"{prefix}llm/openai/api-key",
            "anthropic": f"{prefix}llm/anthropic/api-key",
            "gemini": f"{prefix}llm/google/api-key",
        }

        keys = {}

        # Fetch each secret
        for provider, secret_name in secret_names.items():
            try:
                response = client.get_secret_value(SecretId=secret_name)
                keys[provider] = response['SecretString']
                logger.info(f"{provider.upper()} API key loaded from AWS Secrets Manager")
            except ClientError as e:
                logger.error(f"Failed to load {provider.upper()} key from AWS: {e}")
                keys[provider] = None

        return keys

    except Exception as e:
        logger.error(f"AWS Secrets Manager access failed: {e}")
        logger.warning("Falling back to environment variables")
        return _get_keys_from_env()


def get_llm_config() -> Dict[str, any]:
    """
    Get LLM configuration settings

    Returns:
        Dict with LLM configuration
    """
    return {
        "timeout": Config.LLM_TIMEOUT,
        "max_retries": Config.LLM_MAX_RETRIES,
        "default_temperature": Config.LLM_DEFAULT_TEMPERATURE,
        "default_max_tokens": Config.LLM_DEFAULT_MAX_TOKENS,
    }


# Export config instance
config = Config()
