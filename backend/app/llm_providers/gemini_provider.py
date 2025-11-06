"""
Google Gemini Provider Implementation

Supports:
- Gemini 2.0 Flash
- Gemini 2.0 Flash Lite
- Retry logic with exponential backoff
- Cost calculation
"""

import logging
import time
import asyncio
from typing import Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from .base import LLMProvider
from .models import GenerationResponse
from .pricing import calculate_cost, MODEL_MAPPINGS

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Google Gemini LLM Provider

    Supports Gemini 2.0 Flash and Flash Lite models
    """

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize Gemini provider

        Args:
            api_key: Google API key
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            **kwargs: Additional configuration
        """
        super().__init__(api_key, timeout, max_retries, **kwargs)

        # Configure Gemini
        genai.configure(api_key=api_key)

        logger.info("Gemini provider initialized")

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> GenerationResponse:
        """
        Generate text using Gemini models

        Args:
            prompt: Input prompt
            model: Model identifier (e.g., "gemini-2.0-flash")
            temperature: Temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            GenerationResponse

        Raises:
            Exception: If generation fails
        """
        start_time = time.time()

        try:
            # Get API model name
            api_model = MODEL_MAPPINGS.get(model, model)

            # Call Gemini API with retry logic
            response = await self._generate_with_retry(
                prompt=prompt,
                model=api_model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            latency = time.time() - start_time

            # Extract response data
            generated_text = response.text if hasattr(response, 'text') else ""

            # Gemini provides token counts in usage_metadata
            usage = response.usage_metadata if hasattr(response, 'usage_metadata') else None

            if usage:
                input_tokens = getattr(usage, 'prompt_token_count', 0)
                output_tokens = getattr(usage, 'candidates_token_count', 0)
            else:
                # Fallback: estimate tokens
                input_tokens = len(prompt.split()) * 1.3  # Rough estimate
                output_tokens = len(generated_text.split()) * 1.3
                input_tokens = int(input_tokens)
                output_tokens = int(output_tokens)

            # Get finish reason
            finish_reason = None
            if hasattr(response, 'candidates') and response.candidates:
                finish_reason = str(response.candidates[0].finish_reason) if hasattr(response.candidates[0], 'finish_reason') else None

            # Calculate cost
            cost = calculate_cost(
                model_id=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )

            # Create normalized response
            gen_response = self._create_response(
                generated_text=generated_text,
                model_name=model,
                provider="gemini",
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
            self._log_generation(model, prompt, gen_response)

            return gen_response

        except Exception as e:
            latency = time.time() - start_time
            error_msg = str(e)

            logger.error(f"Gemini generation failed: {error_msg}")

            # Return error response
            return self._create_response(
                generated_text="",
                model_name=model,
                provider="gemini",
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
            Gemini API response

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                # Initialize model
                gemini_model = genai.GenerativeModel(model)

                # Configure generation
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )

                # Generate content (synchronous call wrapped in asyncio)
                response = await asyncio.to_thread(
                    gemini_model.generate_content,
                    prompt,
                    generation_config=generation_config
                )

                return response

            except google_exceptions.ResourceExhausted as e:
                logger.warning(f"Gemini rate limit hit (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
                # Exponential backoff
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)

            except google_exceptions.DeadlineExceeded as e:
                logger.warning(f"Gemini timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Gemini error: {e}")
                raise

    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        **kwargs
    ) -> float:
        """
        Calculate cost for Gemini generation

        Args:
            model: Model identifier
            input_tokens: Input tokens
            output_tokens: Output tokens
            **kwargs: Additional parameters (not used for Gemini)

        Returns:
            Cost in USD
        """
        return calculate_cost(
            model_id=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
