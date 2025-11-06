"""
Pydantic models for LLM provider responses and requests
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class GenerationResponse(BaseModel):
    """
    Normalized response format for all LLM providers
    """
    generated_text: str = Field(..., description="Generated text from the LLM")
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")
    total_tokens: int = Field(..., description="Total tokens (input + output)")
    cost: float = Field(..., description="Cost in USD for this generation")
    latency: float = Field(..., description="Generation latency in seconds")
    model_name: str = Field(..., description="Model used for generation")
    provider: str = Field(..., description="Provider name (openai, anthropic, gemini)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    error: Optional[str] = Field(None, description="Error message if generation failed")

    # Optional metadata
    temperature: Optional[float] = Field(None, description="Temperature used")
    max_tokens: Optional[int] = Field(None, description="Max tokens requested")
    finish_reason: Optional[str] = Field(None, description="Reason generation stopped")

    class Config:
        json_schema_extra = {
            "example": {
                "generated_text": "Sample generated news article...",
                "input_tokens": 450,
                "output_tokens": 150,
                "total_tokens": 600,
                "cost": 0.086,
                "latency": 8.3,
                "model_name": "gpt-4o",
                "provider": "openai",
                "timestamp": "2025-11-04T10:30:00Z",
                "error": None,
                "temperature": 0.7,
                "max_tokens": 500,
                "finish_reason": "stop"
            }
        }


class GenerationRequest(BaseModel):
    """
    Request model for generating news
    """
    trigger_name: str = Field(..., description="Trigger name (e.g., '52wk_high')")
    stock_id: str = Field(..., description="Stock symbol (e.g., 'AAPL')")
    prompt_type: str = Field(..., description="Prompt type: 'paid', 'unpaid', or 'crawler'")
    model_id: str = Field(default="gpt-4o", description="Model identifier")
    temperature: Optional[float] = Field(0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(500, description="Maximum tokens to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "trigger_name": "52wk_high",
                "stock_id": "AAPL",
                "prompt_type": "paid",
                "model_id": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
