"""
Pydantic model for prompt_versions collection
Enables rollback to previous configurations (Story 5.4)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class PromptVersion(BaseModel):
    """
    Version history for trigger prompt configurations.

    Purpose:
    - Rollback: Undo bad configurations instantly
    - Audit Trail: See who published what and when
    - Debugging: Compare versions to find what changed
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trigger_name": "earnings_result",
                "version": 3,
                "llm_config": {
                    "provider": "claude",
                    "model": "claude-sonnet-4-5-20250929",
                    "temperature": 0.7,
                    "max_tokens": 20000
                },
                "data_config": {
                    "data_mode": "new",
                    "sections": [1, 2, 3, 5, 7, 9, 12],
                    "section_order": [1, 2, 3, 5, 7, 9, 12]
                },
                "prompts": {
                    "paid": "Generate detailed article...",
                    "unpaid": "Generate brief summary...",
                    "crawler": "SEO content..."
                },
                "published_by": "john.doe@company.com",
                "test_generation_count": 12,
                "avg_cost_per_generation": 0.045,
                "iteration_count": 5
            }
        }
    )

    # Identifiers
    trigger_name: str
    version: int

    # Full snapshot of configuration at publish time
    llm_config: Dict[str, Any]  # Renamed from model_config
    data_config: Dict[str, Any]
    prompts: Dict[str, Any]  # All 3 types (paid, unpaid, crawler)

    # Audit metadata
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_by: str

    # Usage statistics (from preview phase before publish)
    test_generation_count: Optional[int] = 0
    avg_cost_per_generation: Optional[float] = 0.0
    iteration_count: Optional[int] = 0
