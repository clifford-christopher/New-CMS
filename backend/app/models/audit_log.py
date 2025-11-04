"""
Pydantic model for NEW audit_log collection
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Dict


class AuditLog(BaseModel):
    """NEW collection for change tracking"""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    user_id: str
    action: str  # "created", "updated", "published", "prompt_edited"
    trigger_key: str
    timestamp: datetime
    details: Dict  # JSON diff or action details
