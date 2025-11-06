"""
OpenAI Provider Implementation

Supports:
- GPT-4o, GPT-4o-mini
- GPT-4.1, GPT-4.1-mini, GPT-4.1-nano
- Prompt caching support
- Retry logic with exponential backoff
- Cost calculation
"""

import logging
import time
from typing import Optional

from openai import AsyncOpenAI, OpenAIError, APITimeoutError, RateLimitError

from .base import LLMProvider
from .models import GenerationResponse
from .pricing import calculate_cost

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM Provider

    Supports GPT-4o, GPT-4o-mini, GPT-4.1 series models
    """

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(api_key, timeout, max_retries, **kwargs)

        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )

        logger.info("OpenAI provider initialized")

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> GenerationResponse:
        """
        Generate text using OpenAI models

        Args:
            prompt: Input prompt
            model: Model identifier (e.g., "gpt-4o")
            temperature: Temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            GenerationResponse

        Raises:
            OpenAIError: If generation fails
        """
        start_time = time.time()

        try:
            # Call OpenAI API with retry logic
            response = await self._generate_with_retry(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            latency = time.time() - start_time

            # Extract response data
            generated_text = response.choices[0].message.content or ""
            finish_reason = response.choices[0].finish_reason

            # Extract token counts
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens

            # Handle prompt_tokens_details (can be dict or Pydantic object)
            prompt_tokens_details = getattr(usage, "prompt_tokens_details", None)
            if prompt_tokens_details:
                # Try to access as object attribute first, then as dict
                cached_tokens = getattr(prompt_tokens_details, "cached_tokens", None)
                if cached_tokens is None and isinstance(prompt_tokens_details, dict):
                    cached_tokens = prompt_tokens_details.get("cached_tokens", 0)
                cached_tokens = cached_tokens or 0
            else:
                cached_tokens = 0

            # Calculate cost
            cost = calculate_cost(
                model_id=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_input_tokens=cached_tokens
            )

            # Create normalized response
            gen_response = self._create_response(
                generated_text=generated_text,
                model_name=model,
                provider="openai",
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
            self._log_generation(model, prompt, gen_response, cached_tokens=cached_tokens)

            return gen_response

        except Exception as e:
            latency = time.time() - start_time
            error_msg = str(e)

            logger.error(f"OpenAI generation failed: {error_msg}")

            # Return error response
            return self._create_response(
                generated_text="",
                model_name=model,
                provider="openai",
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
            model: Model name
            temperature: Temperature
            max_tokens: Max tokens
            **kwargs: Additional parameters

        Returns:
            OpenAI API response

        Raises:
            OpenAIError: If all retries fail
        """
        # Retry decorator is applied via tenacity
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
                return response

            except RateLimitError as e:
                logger.warning(f"OpenAI rate limit hit (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
                # Exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

            except APITimeoutError as e:
                logger.warning(f"OpenAI timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1)

            except OpenAIError as e:
                logger.error(f"OpenAI error: {e}")
                raise

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        **kwargs
    ) -> float:
        """
        Calculate cost for OpenAI generation

        Args:
            model: Model identifier
            input_tokens: Input tokens
            output_tokens: Output tokens
            **kwargs: cached_input_tokens (optional)

        Returns:
            Cost in USD
        """
        cached_input_tokens = kwargs.get("cached_input_tokens", 0)

        return calculate_cost(
            model_id=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_input_tokens=cached_input_tokens
        )


# Import asyncio for sleep
import asyncio
