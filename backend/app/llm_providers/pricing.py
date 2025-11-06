"""
LLM Provider Pricing Constants

Updated: 2025-11-04
Pricing is per 1 million tokens (MTok) unless otherwise specified.

Note: Prices subject to change. Update regularly from provider documentation.
- OpenAI: https://openai.com/pricing
- Anthropic: https://www.anthropic.com/pricing
- Google: https://ai.google.dev/pricing
"""

from typing import Dict, Any

# Pricing in USD per 1 million tokens
PRICING: Dict[str, Dict[str, float]] = {
    # ========================================================================
    # OpenAI Models (per 1M tokens)
    # ========================================================================
    "gpt-4.1": {
        "input": 2.00,
        "cached_input": 0.50,
        "output": 8.00,
    },
    "gpt-4.1-mini": {
        "input": 0.40,
        "cached_input": 0.10,
        "output": 1.60,
    },
    "gpt-4.1-nano": {
        "input": 0.10,
        "cached_input": 0.025,
        "output": 0.40,
    },
    "gpt-4o": {
        "input": 2.50,
        "cached_input": 1.25,
        "output": 10.00,
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "cached_input": 0.075,
        "output": 0.60,
    },

    # ========================================================================
    # Anthropic Models (per 1M tokens)
    # With prompt caching support
    # ========================================================================
    "claude-opus-4-1": {
        "input": 15.00,
        "cache_writes_5m": 18.75,    # 5-minute cache write
        "cache_writes_1h": 30.00,    # 1-hour cache write
        "cache_hits": 1.50,          # Cache hit/refresh
        "output": 75.00,
    },
    "claude-opus-4": {
        "input": 15.00,
        "cache_writes_5m": 18.75,
        "cache_writes_1h": 30.00,
        "cache_hits": 1.50,
        "output": 75.00,
    },
    "claude-sonnet-4-5": {
        "input": 3.00,
        "cache_writes_5m": 3.75,
        "cache_writes_1h": 6.00,
        "cache_hits": 0.30,
        "output": 15.00,
    },
    "claude-sonnet-4": {
        "input": 3.00,
        "cache_writes_5m": 3.75,
        "cache_writes_1h": 6.00,
        "cache_hits": 0.30,
        "output": 15.00,
    },
    "claude-haiku-4-5": {
        "input": 1.00,
        "cache_writes_5m": 1.25,
        "cache_writes_1h": 2.00,
        "cache_hits": 0.10,
        "output": 5.00,
    },
    "claude-haiku-3-5": {
        "input": 0.80,
        "cache_writes_5m": 1.00,
        "cache_writes_1h": 1.60,
        "cache_hits": 0.08,
        "output": 4.00,
    },
    "claude-haiku-3": {
        "input": 0.25,
        "cache_writes_5m": 0.30,
        "cache_writes_1h": 0.50,
        "cache_hits": 0.03,
        "output": 1.25,
    },

    # ========================================================================
    # Google Gemini Models (per 1M tokens)
    # ========================================================================
    "gemini-2.0-flash": {
        "input": 0.10,
        "output": 0.40,
    },
    "gemini-2.0-flash-lite": {
        "input": 0.075,
        "output": 0.30,
    },
}


# Model name mappings (friendly name -> API model identifier)
MODEL_MAPPINGS: Dict[str, str] = {
    # OpenAI
    "gpt-4.1": "gpt-4.1",
    "gpt-4.1-mini": "gpt-4.1-mini",
    "gpt-4.1-nano": "gpt-4.1-nano",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",

    # Anthropic (exact model IDs from API)
    "claude-opus-4-1": "claude-opus-4-1-20250514",
    "claude-opus-4": "claude-opus-4-20250514",
    "claude-sonnet-4-5": "claude-sonnet-4-5-20250929",
    "claude-sonnet-4": "claude-sonnet-4-20250514",
    "claude-haiku-4-5": "claude-haiku-4-5-20250112",
    "claude-haiku-3-5": "claude-3-5-haiku-20241022",
    "claude-haiku-3": "claude-3-haiku-20240307",

    # Google Gemini
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gemini-2.0-flash-lite": "gemini-2.0-flash-lite",
}


def calculate_cost(
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    cached_input_tokens: int = 0,
    cache_writes: int = 0,
    cache_hits: int = 0
) -> float:
    """
    Calculate cost in USD for a generation

    Args:
        model_id: Model identifier (e.g., "gpt-4o", "claude-sonnet-4-5")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cached_input_tokens: Number of cached input tokens (OpenAI)
        cache_writes: Number of cache write tokens (Anthropic)
        cache_hits: Number of cache hit tokens (Anthropic)

    Returns:
        Cost in USD

    Raises:
        ValueError: If model_id is not found in pricing
    """
    if model_id not in PRICING:
        raise ValueError(f"Model '{model_id}' not found in pricing. Available models: {list(PRICING.keys())}")

    pricing = PRICING[model_id]

    # Convert tokens to millions
    input_m = input_tokens / 1_000_000
    output_m = output_tokens / 1_000_000
    cached_input_m = cached_input_tokens / 1_000_000
    cache_writes_m = cache_writes / 1_000_000
    cache_hits_m = cache_hits / 1_000_000

    # Calculate cost based on provider
    if "claude" in model_id:
        # Anthropic: separate cache costs
        cost = (
            (input_m * pricing["input"]) +
            (cache_writes_m * pricing.get("cache_writes_5m", 0)) +  # Assuming 5m cache by default
            (cache_hits_m * pricing.get("cache_hits", 0)) +
            (output_m * pricing["output"])
        )
    elif "gpt" in model_id:
        # OpenAI: cached input at reduced rate
        cost = (
            (input_m * pricing["input"]) +
            (cached_input_m * pricing.get("cached_input", pricing["input"])) +
            (output_m * pricing["output"])
        )
    else:
        # Gemini: simple input/output
        cost = (
            (input_m * pricing["input"]) +
            (output_m * pricing["output"])
        )

    return round(cost, 6)  # Round to 6 decimal places


def get_model_info(model_id: str) -> Dict[str, Any]:
    """
    Get model information including pricing

    Args:
        model_id: Model identifier

    Returns:
        Dict with model info
    """
    if model_id not in PRICING:
        return {}

    pricing = PRICING[model_id]

    # Determine provider
    if "gpt" in model_id:
        provider = "openai"
    elif "claude" in model_id:
        provider = "anthropic"
    elif "gemini" in model_id:
        provider = "gemini"
    else:
        provider = "unknown"

    return {
        "model_id": model_id,
        "provider": provider,
        "pricing": pricing,
        "api_model_name": MODEL_MAPPINGS.get(model_id, model_id)
    }
