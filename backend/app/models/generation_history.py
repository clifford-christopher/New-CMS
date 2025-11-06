"""
Pydantic model for generation_history collection
Tracks all news generation attempts (preview + production)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class GenerationHistory(BaseModel):
    """
    Generation history for preview and production news.

    Used for:
    - Analytics (costs, performance, success rates)
    - Debugging (replay exact inputs that caused issues)
    - A/B Testing (compare NEW vs LEGACY methods)
    - Cost tracking (per-trigger, per-model)
    """
    # Identifiers
    trigger_name: str
    stock_id: str  # Changed from stockid to match API convention
    prompt_type: str  # "paid" | "unpaid" | "crawler"
    data_mode: str  # "OLD" | "NEW" | "OLD_NEW"

    # Model information
    model: str  # e.g., "claude-sonnet-4-5", "gpt-4o"
    provider: str  # "openai", "anthropic", "gemini"

    # Prompts (truncated for storage)
    prompt_template: str = Field(..., description="Original prompt template (truncated to 1000 chars)")
    final_prompt: str = Field(..., description="Final prompt after substitution (truncated to 1000 chars)")

    # Generated output
    generated_text: str  # Full generated text

    # Token usage
    input_tokens: int
    output_tokens: int
    total_tokens: int

    # Cost and performance
    cost: float  # USD
    latency: float  # seconds (renamed from generation_time)

    # Metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: Optional[str] = None

    # Error tracking
    error: Optional[str] = None  # Renamed from error_message

    # Additional metadata
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    finish_reason: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trigger_name": "52wk_high",
                "stock_id": "AAPL",
                "prompt_type": "paid",
                "data_mode": "OLD_NEW",
                "model": "gpt-4o",
                "provider": "openai",
                "prompt_template": "Generate a news article about {{stock_id}}...",
                "final_prompt": "Generate a news article about AAPL reaching new highs...",
                "generated_text": "Apple Inc. (AAPL) reached a 52-week high today...",
                "input_tokens": 450,
                "output_tokens": 150,
                "total_tokens": 600,
                "cost": 0.086,
                "latency": 8.3,
                "timestamp": "2025-11-04T10:30:00Z",
                "session_id": "abc-123-def",
                "error": None,
                "temperature": 0.7,
                "max_tokens": 500,
                "finish_reason": "stop"
            }
        }
    )


class GenerationHistoryResponse(BaseModel):
    """
    Response model for generation history queries
    """
    generations: list[GenerationHistory]
    total: int
    page: int = 1
    page_size: int = 10

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "generations": [],
                "total": 25,
                "page": 1,
                "page_size": 10
            }
        }
    )
