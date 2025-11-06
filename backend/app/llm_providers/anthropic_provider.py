"""
Anthropic Provider Implementation

Supports:
- Claude Sonnet 4.5, Claude Haiku 4.5
- Claude Opus 4.1, Claude Opus 4
- Prompt caching support
- Retry logic with exponential backoff
- Cost calculation with cache tokens
"""

import logging
import time
import asyncio
from typing import Optional

from anthropic import AsyncAnthropic, AnthropicError, APITimeoutError, RateLimitError

from .base import LLMProvider
from .models import GenerationResponse
from .pricing import calculate_cost, MODEL_MAPPINGS

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """
    Anthropic LLM Provider

    Supports Claude Sonnet, Haiku, and Opus models with prompt caching
    """

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(api_key, timeout, max_retries, **kwargs)

        # Initialize Anthropic client
        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )

        logger.info("Anthropic provider initialized")

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> GenerationResponse:
        """
        Generate text using Anthropic models

        Args:
            prompt: Input prompt
            model: Model identifier (e.g., "claude-sonnet-4-5")
            temperature: Temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (system prompt, etc.)

        Returns:
            GenerationResponse

        Raises:
            AnthropicError: If generation fails
        """
        start_time = time.time()

        try:
            # Get API model name
            api_model = MODEL_MAPPINGS.get(model, model)

            # Call Anthropic API with retry logic
            response = await self._generate_with_retry(
                prompt=prompt,
                model=api_model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            latency = time.time() - start_time

            # Extract response data
            generated_text = response.content[0].text if response.content else ""
            finish_reason = response.stop_reason

            # Extract token counts
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # Anthropic provides cache token details
            cache_creation_tokens = getattr(response.usage, "cache_creation_input_tokens", 0) or 0
            cache_read_tokens = getattr(response.usage, "cache_read_input_tokens", 0) or 0

            # Calculate cost
            cost = calculate_cost(
                model_id=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_writes=cache_creation_tokens,
                cache_hits=cache_read_tokens
            )

            # Create normalized response
            gen_response = self._create_response(
                generated_text=generated_text,
                model_name=model,
                provider="anthropic",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                latency=latency,
                temperature=temperature,
                max_tokens=max_tokens,
                finish_reason=finish_reason,
                error=None
            )

            # Log generation
            self._log_generation(
                model,
                prompt,
                gen_response,
                cache_creation_tokens=cache_creation_tokens,
                cache_read_tokens=cache_read_tokens
            )

            return gen_response

        except Exception as e:
            latency = time.time() - start_time
            error_msg = str(e)

            logger.error(f"Anthropic generation failed: {error_msg}")

            # Return error response
            return self._create_response(
                generated_text="",
                model_name=model,
                provider="anthropic",
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                latency=latency,
                temperature=temperature,
                max_tokens=max_tokens,
                finish_reason="error",
                error=error_msg
            )

    async def _generate_with_retry(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ):
        """
        Generate with retry logic

        Args:
            prompt: Input prompt
            model: API model name
            temperature: Temperature
            max_tokens: Max tokens
            **kwargs: Additional parameters

        Returns:
            Anthropic API response

        Raises:
            AnthropicError: If all retries fail
        """
        system_prompt = kwargs.get("system", None)

        for attempt in range(self.max_retries):
            try:
                # Build messages
                messages = [
                    {"role": "user", "content": prompt}
                ]

                # Build API parameters
                api_params = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }

                # Only include system if it has a value (Anthropic doesn't accept None)
                if system_prompt:
                    api_params["system"] = system_prompt

                # Call Anthropic API
                response = await self.client.messages.create(**api_params)
                return response

            except RateLimitError as e:
                logger.warning(f"Anthropic rate limit hit (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
                # Exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

            except APITimeoutError as e:
                logger.warning(f"Anthropic timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1)

            except AnthropicError as e:
                logger.error(f"Anthropic error: {e}")
                raise

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        **kwargs
    ) -> float:
        """
        Calculate cost for Anthropic generation

        Args:
            model: Model identifier
            input_tokens: Input tokens
            output_tokens: Output tokens
            **kwargs: cache_writes, cache_hits (optional)

        Returns:
            Cost in USD
        """
        cache_writes = kwargs.get("cache_writes", 0)
        cache_hits = kwargs.get("cache_hits", 0)

        return calculate_cost(
            model_id=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_writes=cache_writes,
            cache_hits=cache_hits
        )
