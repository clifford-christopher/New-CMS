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
    stockid: int
    prompt_type: str  # "paid" | "unpaid" | "crawler"
    data_mode: str  # "old" | "new" | "old_new"
    model: str  # e.g., "claude-sonnet-4-5-20250929", "gpt-4o"

    # Input data
    input_data: Dict[str, Any]  # Merged data used for generation
    prompt_used: str  # Final prompt with substitutions

    # Output
    generated_html: str  # Full HTML output from LLM
    extracted_title: str
    extracted_summary: str
    extracted_article: str

    # Metadata
    method: str  # "new" | "legacy"
    tokens_used: int
    cost: float  # USD
    generation_time: float  # seconds
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str  # "success" | "failed"
    error_message: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trigger_name": "earnings_result",
                "stockid": 513374,
                "prompt_type": "paid",
                "data_mode": "new",
                "model": "claude-sonnet-4-5-20250929",
                "input_data": {
                    "company_name": "Acme Corp",
                    "sections": {...}
                },
                "prompt_used": "Generate detailed article for Acme Corp...",
                "generated_html": "<html>...</html>",
                "extracted_title": "Acme Corp Reports Strong Q3 Earnings",
                "extracted_summary": "...",
                "extracted_article": "...",
                "method": "new",
                "tokens_used": 15234,
                "cost": 0.0523,
                "generation_time": 3.2,
                "status": "success"
            }
        }
    )
