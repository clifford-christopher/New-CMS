"""
Published Configuration Model
Story 5.2: Configuration Publishing with Confirmation

MongoDB schema for storing published trigger configurations
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class TestResultsSummary(BaseModel):
    """Summary of test results for a prompt type"""
    models_tested: List[str]
    avg_cost: float
    avg_latency: float
    total_tests: int
    sample_output_preview: Optional[str] = None  # First 200 chars of generated text


class PublishedConfiguration(BaseModel):
    """
    Published configuration for a trigger

    Represents a snapshot of the configuration at the time of publishing,
    including all prompts, APIs, sections, model settings, and test metadata.
    """

    # Identification
    trigger_id: str = Field(..., description="Trigger identifier")
    version: int = Field(..., description="Auto-incremented version number")

    # Configuration snapshot
    apis: List[str] = Field(default_factory=list, description="List of API identifiers")
    section_order: List[str] = Field(default_factory=list, description="Ordered list of section IDs")
    prompts: Dict[str, str] = Field(default_factory=dict, description="Prompt templates by type (paid, unpaid, crawler)")

    # Model settings
    model_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Model configuration (selected_models, temperature, max_tokens)"
    )

    # Test metadata (NEW for Story 5.2)
    test_results_summary: Dict[str, TestResultsSummary] = Field(
        default_factory=dict,
        description="Test results summary by prompt type"
    )

    # Status
    is_active: bool = Field(default=True, description="Whether this is the active published configuration")

    # Metadata
    published_at: datetime = Field(default_factory=datetime.utcnow, description="Publication timestamp")
    published_by: str = Field(..., description="User ID who published")

    class Config:
        json_schema_extra = {
            "example": {
                "trigger_id": "earnings",
                "version": 5,
                "apis": ["earnings_api", "price_data_api"],
                "section_order": ["company_overview", "financial_data", "analysis"],
                "prompts": {
                    "paid": "Generate a detailed article about {{company}}...",
                    "unpaid": "Generate a brief article about {{company}}...",
                    "crawler": "Generate SEO-optimized article about {{company}}..."
                },
                "model_settings": {
                    "selected_models": ["gpt-4o", "claude-3.5-sonnet"],
                    "temperature": 0.7,
                    "max_tokens": 500
                },
                "test_results_summary": {
                    "paid": {
                        "models_tested": ["gpt-4o", "claude-3.5-sonnet"],
                        "avg_cost": 0.42,
                        "avg_latency": 8.5,
                        "total_tests": 2,
                        "sample_output_preview": "Apple Inc. reported strong earnings..."
                    }
                },
                "is_active": True,
                "published_at": "2025-11-06T14:30:00Z",
                "published_by": "user123"
            }
        }


class PublishRequest(BaseModel):
    """Request payload for publishing configuration"""

    # Configuration data
    apis: List[str]
    section_order: List[str]
    prompts: Dict[str, str]
    model_settings: Dict[str, Any]

    # Test metadata
    test_results_summary: Dict[str, TestResultsSummary]

    # User info
    published_by: str

    # Optional reason/notes
    notes: Optional[str] = None


class PublishResponse(BaseModel):
    """Response after successful publish"""

    success: bool
    message: str
    trigger_id: str
    version: int
    published_at: datetime
    is_active: bool
