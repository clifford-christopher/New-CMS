"""
LLM Providers Module

This module provides a unified abstraction layer for multiple LLM providers:
- OpenAI (GPT-4o, GPT-4o-mini, etc.)
- Anthropic (Claude Sonnet 4.5, Claude Haiku 4.5, etc.)
- Google Gemini (2.0-flash, 2.0-flash-lite)

All providers implement the LLMProvider abstract base class with:
- generate() method for text generation
- calculate_cost() method for cost estimation
- Normalized response format
- Retry logic with exponential backoff
- Comprehensive logging
"""

from .base import LLMProvider
from .models import GenerationResponse, GenerationRequest
from .registry import ProviderRegistry, initialize_registry
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider

__all__ = [
    "LLMProvider",
    "GenerationResponse",
    "GenerationRequest",
    "ProviderRegistry",
    "OpenAIProvider",
    "AnthropicProvider",
    "GeminiProvider",
]

# Initialize the provider registry
initialize_registry()
