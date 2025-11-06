"""
Provider Registry

Centralized registry for all LLM providers.
Provides:
- Model lookup by ID
- Provider instantiation
- Model listing for UI
"""

import logging
from typing import Dict, List, Type, Any, Tuple

from .base import LLMProvider
from .pricing import PRICING, MODEL_MAPPINGS, get_model_info

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """
    Registry for all LLM providers

    Maps model IDs to provider classes and handles provider instantiation.
    """

    # Model ID -> (ProviderClass, API Model Name)
    # Will be populated after provider classes are imported
    _MODEL_REGISTRY: Dict[str, Tuple[Type[LLMProvider], str]] = {}

    # Provider name -> Provider class
    _PROVIDER_CLASSES: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register_provider(
        cls,
        provider_name: str,
        provider_class: Type[LLMProvider]
    ) -> None:
        """
        Register a provider class

        Args:
            provider_name: Provider name (e.g., "openai", "anthropic")
            provider_class: Provider class
        """
        cls._PROVIDER_CLASSES[provider_name] = provider_class
        logger.info(f"Registered LLM provider: {provider_name}")

    @classmethod
    def register_model(
        cls,
        model_id: str,
        provider_class: Type[LLMProvider],
        api_model_name: str
    ) -> None:
        """
        Register a model

        Args:
            model_id: Model identifier (e.g., "gpt-4o", "claude-sonnet-4-5")
            provider_class: Provider class to use
            api_model_name: Actual API model name
        """
        cls._MODEL_REGISTRY[model_id] = (provider_class, api_model_name)
        logger.debug(f"Registered model: {model_id} -> {provider_class.__name__}")

    @classmethod
    def get_provider(
        cls,
        model_id: str,
        api_key: str,
        config: Dict[str, Any] = None
    ) -> LLMProvider:
        """
        Get provider instance for a model

        Args:
            model_id: Model identifier
            api_key: API key for the provider
            config: Optional configuration dict

        Returns:
            Provider instance

        Raises:
            ValueError: If model_id not found in registry
        """
        if model_id not in cls._MODEL_REGISTRY:
            available = list(cls._MODEL_REGISTRY.keys())
            raise ValueError(
                f"Model '{model_id}' not found in registry. "
                f"Available models: {available}"
            )

        provider_class, api_model_name = cls._MODEL_REGISTRY[model_id]

        # Merge default config with provided config
        final_config = config or {}

        # Instantiate provider
        provider = provider_class(api_key=api_key, **final_config)

        logger.info(f"Instantiated provider for model: {model_id} (API: {api_model_name})")

        return provider

    @classmethod
    def list_available_models(cls) -> List[Dict[str, Any]]:
        """
        List all available models with metadata

        Returns:
            List of model info dicts
        """
        models = []

        for model_id, (provider_class, api_model_name) in cls._MODEL_REGISTRY.items():
            model_info = get_model_info(model_id)

            # Add provider class name
            model_info["provider_class"] = provider_class.__name__

            # Add display name
            model_info["display_name"] = cls._get_display_name(model_id)

            # Add description
            model_info["description"] = cls._get_description(model_id)

            models.append(model_info)

        # Sort by provider, then by price
        models.sort(key=lambda x: (x["provider"], x["pricing"].get("input", 0)))

        return models

    @classmethod
    def list_models_by_provider(cls, provider: str) -> List[Dict[str, Any]]:
        """
        List models for a specific provider

        Args:
            provider: Provider name ("openai", "anthropic", "gemini")

        Returns:
            List of model info dicts
        """
        all_models = cls.list_available_models()
        return [m for m in all_models if m["provider"] == provider]

    @classmethod
    def get_model_api_name(cls, model_id: str) -> str:
        """
        Get API model name for a model ID

        Args:
            model_id: Model identifier

        Returns:
            API model name

        Raises:
            ValueError: If model not found
        """
        if model_id not in cls._MODEL_REGISTRY:
            raise ValueError(f"Model '{model_id}' not found in registry")

        return cls._MODEL_REGISTRY[model_id][1]

    @staticmethod
    def _get_display_name(model_id: str) -> str:
        """Get display-friendly name for model"""
        display_names = {
            # OpenAI
            "gpt-4.1": "GPT-4.1",
            "gpt-4.1-mini": "GPT-4.1 Mini",
            "gpt-4.1-nano": "GPT-4.1 Nano",
            "gpt-4o": "GPT-4o",
            "gpt-4o-mini": "GPT-4o Mini",

            # Anthropic
            "claude-opus-4-1": "Claude Opus 4.1",
            "claude-opus-4": "Claude Opus 4",
            "claude-sonnet-4-5": "Claude Sonnet 4.5",
            "claude-sonnet-4": "Claude Sonnet 4",
            "claude-haiku-4-5": "Claude Haiku 4.5",
            "claude-haiku-3-5": "Claude Haiku 3.5",
            "claude-haiku-3": "Claude Haiku 3",

            # Gemini
            "gemini-2.0-flash": "Gemini 2.0 Flash",
            "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite",
        }
        return display_names.get(model_id, model_id)

    @staticmethod
    def _get_description(model_id: str) -> str:
        """Get description for model"""
        descriptions = {
            # OpenAI
            "gpt-4o": "Most capable OpenAI model, best for complex tasks",
            "gpt-4o-mini": "Fast and affordable, good for simple tasks",

            # Anthropic
            "claude-sonnet-4-5": "Balanced performance and cost, recommended",
            "claude-haiku-4-5": "Fast and affordable, good for testing",

            # Gemini
            "gemini-2.0-flash": "Google's latest flash model",
            "gemini-2.0-flash-lite": "Lightest Gemini model, lowest cost",
        }
        return descriptions.get(model_id, "")


# Initialize registry after all providers are imported
def initialize_registry():
    """
    Initialize the provider registry with all available models

    This function is called after all provider classes are imported.
    """
    # Import provider classes here to avoid circular imports
    try:
        from .openai_provider import OpenAIProvider
        from .anthropic_provider import AnthropicProvider
        from .gemini_provider import GeminiProvider

        # Register providers
        ProviderRegistry.register_provider("openai", OpenAIProvider)
        ProviderRegistry.register_provider("anthropic", AnthropicProvider)
        ProviderRegistry.register_provider("gemini", GeminiProvider)

        # Register OpenAI models
        for model_id in ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-4o-mini"]:
            api_name = MODEL_MAPPINGS.get(model_id, model_id)
            ProviderRegistry.register_model(model_id, OpenAIProvider, api_name)

        # Register Anthropic models
        for model_id in [
            "claude-opus-4-1", "claude-opus-4",
            "claude-sonnet-4-5", "claude-sonnet-4",
            "claude-haiku-4-5", "claude-haiku-3-5", "claude-haiku-3"
        ]:
            api_name = MODEL_MAPPINGS.get(model_id, model_id)
            ProviderRegistry.register_model(model_id, AnthropicProvider, api_name)

        # Register Gemini models
        for model_id in ["gemini-2.0-flash", "gemini-2.0-flash-lite"]:
            api_name = MODEL_MAPPINGS.get(model_id, model_id)
            ProviderRegistry.register_model(model_id, GeminiProvider, api_name)

        logger.info("Provider registry initialized successfully")

    except ImportError as e:
        logger.warning(f"Could not initialize provider registry: {e}")
        logger.warning("Provider classes may not be implemented yet")
