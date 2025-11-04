"""
Example Pydantic model for demonstrating shared schema pattern.
This file shows how schemas can be shared between frontend and backend.
"""
from pydantic import BaseModel
from typing import Optional


class ExampleModel(BaseModel):
    """
    Example model demonstrating the monorepo shared schema pattern.

    This model can be:
    - Imported by backend Python code
    - Converted to TypeScript types for frontend

    Actual shared schemas will be defined in later stories when data models are finalized.
    """
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "example_001",
                "name": "Example Item",
                "description": "This is an example description"
            }
        }
