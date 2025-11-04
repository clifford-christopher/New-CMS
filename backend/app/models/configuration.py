"""
Pydantic models for NEW configurations collection
WRITE/UPDATE - for CMS-managed prompt configurations with versioning
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Dict, Optional, Any


class PromptVersionHistory(BaseModel):
    """Track prompt changes over time"""
    template: str
    timestamp: datetime
    user_id: str
    notes: Optional[str] = None


class PromptConfig(BaseModel):
    """Prompt configuration with versioning"""
    article: str  # Prompt template
    system: Optional[str] = None
    version_history: List[PromptVersionHistory] = []
    last_test_generation: Optional[Dict[str, Any]] = None


class Configuration(BaseModel):
    """NEW collection for CMS-managed prompt configurations (versioned)"""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    trigger_key: str  # Links to trigger_prompts.trigger_key
    trigger_name: str
    trigger_display_name: str
    version: int

    # Model configuration (mirrors TriggerPrompt.model_config)
    model_config_data: Dict[str, Any] = Field(alias="model_config")

    # Prompts for all three variants
    prompts: Dict[str, PromptConfig]  # {"paid": PromptConfig, "unpaid": PromptConfig, "crawler": PromptConfig}

    # Special handling (mirrors TriggerPrompt.special_handling)
    special_handling: Optional[Dict[str, Any]] = None

    # Metadata
    created_by: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    is_active: bool  # True if this is the active/production version
    cms_managed: bool = True  # Always true for CMS-managed prompts
