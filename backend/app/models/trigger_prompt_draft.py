"""
Pydantic model for trigger_prompt_drafts collection

This collection stores draft/update versions of prompts separately from
the published trigger_prompts collection, enabling:
- Draft/publish workflow
- User attribution for all changes
- Full version history
- No modification of published configurations until explicitly published
- Single document per trigger session (all prompt types together)
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PromptTemplate(BaseModel):
    """Individual prompt template with metadata"""
    template: str = Field(..., min_length=1, description="Prompt template content")
    character_count: int = Field(default=0, ge=0, description="Number of characters")
    word_count: int = Field(default=0, ge=0, description="Number of words")


class PromptTemplates(BaseModel):
    """All prompt types for a trigger (paid, unpaid, crawler)"""
    paid: Optional[PromptTemplate] = None
    unpaid: Optional[PromptTemplate] = None
    crawler: Optional[PromptTemplate] = None


class TriggerPromptDraft(BaseModel):
    """
    Model for prompt draft documents in trigger_prompt_drafts collection

    Single document contains ALL prompt types (paid, unpaid, crawler) for a trigger.
    Each save creates a new version, preserving full history.
    """
    trigger_name: str = Field(..., description="Trigger identifier (e.g., '52wk_high')")
    prompts: PromptTemplates = Field(..., description="All prompt templates (paid, unpaid, crawler)")
    saved_by: str = Field(default="system", description="User ID who saved this draft")
    saved_at: datetime = Field(default_factory=datetime.utcnow, description="When this draft was saved")
    is_draft: bool = Field(default=True, description="Whether this is a draft (unpublished)")
    version: int = Field(default=1, ge=1, description="Version number for this trigger")
    session_id: Optional[str] = Field(default=None, description="Optional session identifier")

    class Config:
        json_schema_extra = {
            "example": {
                "trigger_name": "52wk_high",
                "prompts": {
                    "paid": {
                        "template": "Craft a SEO friendly news article...",
                        "character_count": 450,
                        "word_count": 75
                    },
                    "unpaid": {
                        "template": "Brief summary for unpaid users...",
                        "character_count": 320,
                        "word_count": 52
                    },
                    "crawler": {
                        "template": "Crawler-friendly content...",
                        "character_count": 380,
                        "word_count": 63
                    }
                },
                "saved_by": "user123",
                "saved_at": "2025-11-04T10:30:00Z",
                "is_draft": True,
                "version": 3,
                "session_id": "abc-123-def"
            }
        }


class PromptDraftResponse(BaseModel):
    """Response model after saving prompt drafts"""
    success: bool
    message: str
    draft: dict  # Single draft document
    trigger_name: str
    version: int
