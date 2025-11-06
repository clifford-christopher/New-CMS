"""
Base abstract class for all LLM providers

All provider implementations must inherit from LLMProvider and implement:
- generate() method for text generation
- calculate_cost() method for cost calculation

Includes:
- Retry logic with exponential backoff
- Comprehensive logging
- Normalized response format
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from .models import GenerationResponse

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers

    All providers must implement:
    - generate() for text generation
    - calculate_cost() for cost calculation
    """

    def __init__(
        self,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize LLM provider

        Args:
            api_key: API key for the provider
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.config = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> GenerationResponse:
        """
        Generate text using the LLM

        Args:
            prompt: Input prompt text
            model: Model identifier
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            GenerationResponse with normalized format

        Raises:
            Exception: If generation fails after all retries
        """
        pass

    @abstractmethod
    def calculate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        **kwargs
    ) -> float:
        """
        Calculate cost for a generation

        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            **kwargs: Additional parameters (cached tokens, etc.)

        Returns:
            Cost in USD
        """
        pass

    def _log_generation(
        self,
        model: str,
        prompt: str,
        response: GenerationResponse,
        **kwargs
    ) -> None:
        """
        Log generation details

        Args:
            model: Model used
            prompt: Input prompt (truncated for logging)
            response: Generation response
            **kwargs: Additional metadata to log
        """
        prompt_truncated = prompt[:200] + "..." if len(prompt) > 200 else prompt

        logger.info(
            f"LLM Generation | "
            f"Provider: {response.provider} | "
            f"Model: {model} | "
            f"Tokens: {response.total_tokens} ({response.input_tokens} in + {response.output_tokens} out) | "
            f"Cost: ${response.cost:.6f} | "
            f"Latency: {response.latency:.2f}s | "
            f"Finish: {response.finish_reason or 'N/A'}"
        )

        logger.debug(
            f"LLM Generation Details | "
            f"Prompt: {prompt_truncated} | "
            f"Temperature: {response.temperature} | "
            f"Max Tokens: {response.max_tokens} | "
            f"Generated Length: {len(response.generated_text)} chars"
        )

        if response.error:
            logger.error(f"LLM Generation Error | Model: {model} | Error: {response.error}")

    def _create_response(
        self,
        generated_text: str,
        model_name: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        latency: float,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        finish_reason: Optional[str] = None,
        error: Optional[str] = None
    ) -> GenerationResponse:
        """
        Create normalized GenerationResponse

        Args:
            generated_text: Generated text
            model_name: Model identifier
            provider: Provider name
            input_tokens: Input token count
            output_tokens: Output token count
            cost: Cost in USD
            latency: Latency in seconds
            temperature: Temperature used
            max_tokens: Max tokens requested
            finish_reason: Reason generation stopped
            error: Error message if failed

        Returns:
            GenerationResponse
        """
        return GenerationResponse(
            generated_text=generated_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=cost,
            latency=latency,
            model_name=model_name,
            provider=provider,
            timestamp=datetime.utcnow(),
            temperature=temperature,
            max_tokens=max_tokens,
            finish_reason=finish_reason,
            error=error
        )

    @staticmethod
    def retry_decorator():
        """
        Retry decorator for API calls

        Retries on common transient errors:
        - Connection errors
        - Timeout errors
        - Rate limit errors
        - Server errors (5xx)

        Uses exponential backoff: 1s, 2s, 4s
        """
        return retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((
                ConnectionError,
                TimeoutError,
                # Provider-specific errors should be added in subclasses
            )),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
