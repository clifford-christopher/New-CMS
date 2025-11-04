"""
Pydantic models for News CMS Workflow configuration
Extends trigger_prompts collection with new fields for workflow support
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers (Google removed per requirements)."""
    OPENAI = "openai"
    CLAUDE = "claude"


class DataMode(str, Enum):
    """Data modes for news generation."""
    OLD = "old"  # Existing trigger data from news_triggers
    NEW = "new"  # Generated structured data from generate_full_report.py
    OLD_NEW = "old_new"  # Merge of both


class LLMConfig(BaseModel):
    """LLM model configuration."""
    model_config = ConfigDict(use_enum_values=True)

    provider: LLMProvider
    model: str  # e.g., "claude-sonnet-4-5-20250929", "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=20000, gt=0)


class DataConfig(BaseModel):
    """Data source configuration."""
    model_config = ConfigDict(use_enum_values=True)

    data_mode: DataMode
    sections: Optional[List[int]] = Field(default=None)  # 1-14, only if NEW or OLD_NEW
    section_order: Optional[List[int]] = Field(default=None)  # Must match sections

    @field_validator('sections')
    @classmethod
    def validate_sections(cls, v):
        """Validate sections are 1-14, no duplicates."""
        if v is not None:
            if not all(1 <= s <= 14 for s in v):
                raise ValueError("Sections must be integers between 1 and 14")
            if len(v) != len(set(v)):
                raise ValueError("Sections must not contain duplicates")
        return v

    @field_validator('section_order')
    @classmethod
    def validate_section_order(cls, v, info):
        """Validate section_order matches sections."""
        if v is not None and 'sections' in info.data and info.data['sections'] is not None:
            sections = info.data['sections']
            if sorted(v) != sorted(sections):
                raise ValueError("section_order must contain same values as sections")
        return v


class PromptTemplates(BaseModel):
    """Multi-type prompt templates."""
    paid: str = Field(..., min_length=1)  # Required
    unpaid: Optional[str] = None
    crawler: Optional[str] = None


class TriggerPromptConfig(BaseModel):
    """
    Extended trigger_prompts collection model for News CMS Workflow.

    Backward compatible: Existing documents without new fields will use default values.
    isActive=false means legacy generation method will be used.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "trigger_name": "earnings_result",
                "isActive": True,
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
                    "paid": "Generate detailed article for {{company_name}}...",
                    "unpaid": "Generate brief summary...",
                    "crawler": "SEO content..."
                },
                "version": 1
            }
        }
    )

    trigger_name: str
    isActive: bool = False  # Critical: Controls NEW vs LEGACY workflow
    llm_config: Optional[LLMConfig] = None  # Renamed from model_config
    data_config: Optional[DataConfig] = None
    prompts: Optional[PromptTemplates] = None
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    published_by: Optional[str] = None
