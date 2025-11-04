"""
Pydantic model for NEW users collection
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class User(BaseModel):
    """NEW collection for user management"""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    username: str
    email: str
    role: str  # "content_manager" | "analyst" | "team_lead"
    created_at: datetime
