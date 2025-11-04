"""
Pydantic models for existing trigger_prompts collection
READ ONLY - matches existing schema with 54 documents
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any


class PromptVariant(BaseModel):
    """Prompt template for paid/unpaid/crawler variants"""
    article: str
    system: Optional[str] = None


class ModelConfig(BaseModel):
    """LLM model configuration"""
    model_name: str  # e.g., "gpt-4o-mini"
    provider: str  # e.g., "openai"
    temperature: float
    max_tokens: int
    cost_per_1m_input_tokens: float
    cost_per_1m_output_tokens: float


class SpecialHandling(BaseModel):
    """Special handling flags for IRB and custom logic"""
    has_irb_boilerplate: bool
    irb_stock_id: Optional[str] = None
    irb_boilerplate_text: Optional[str] = None
    irb_unpaid_override: Optional[str] = None
    irb_crawler_override: Optional[str] = None


class PromptMetadata(BaseModel):
    """Metadata for prompt tracking"""
    created_at: str
    updated_at: str
    version: int
    extracted_from: str  # e.g., "generate_news.py"
    extraction_date: str
    notes: str
    cms_managed: bool  # False for legacy prompts


class PromptStats(BaseModel):
    """Usage statistics"""
    total_generations: int
    last_used: Optional[str] = None
    avg_generation_time_ms: Optional[float] = None
    success_rate: Optional[float] = None


class TriggerPrompt(BaseModel):
    """Model for existing trigger_prompts collection (54 documents) - READ ONLY"""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    trigger_name: str  # e.g., "52_week_high_summary"
    trigger_key: str  # Unique key for lookup
    trigger_display_name: str
    model_config_data: ModelConfig = Field(alias="model_config")
    prompts: Dict[str, PromptVariant]  # {"paid": PromptVariant, "unpaid": PromptVariant, "crawler": PromptVariant}
    special_handling: SpecialHandling
    metadata: PromptMetadata
    stats: PromptStats
