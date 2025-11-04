"""
Pydantic models for structured data generation endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class GenerateRequest(BaseModel):
    """Request model for generating structured data"""
    stock_id: str = Field(..., description="Numeric stock ID (e.g., '399834')")
    sections: List[str] = Field(..., description="List of section IDs to generate (1-14)")

    class Config:
        json_schema_extra = {
            "example": {
                "stock_id": "399834",
                "sections": ["1", "2", "3"]
            }
        }


class SectionData(BaseModel):
    """Model for individual section data"""
    section_id: str = Field(..., description="Section identifier (1-14)")
    section_name: str = Field(..., description="Human-readable section name")
    content: str = Field(..., description="Section content/data")


class JobResponse(BaseModel):
    """Response model when creating a new generation job"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending")
    message: str = Field(..., description="Human-readable message")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "507f1f77bcf86cd799439011",
                "status": "pending",
                "message": "Job created successfully"
            }
        }


class JobStatusResponse(BaseModel):
    """Response model for job status polling"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending, running, completed, failed")
    stock_id: Optional[str] = Field(None, description="Stock ID from request")
    requested_sections: Optional[List[str]] = Field(None, description="Requested section IDs")
    sections_data: Optional[List[SectionData]] = Field(None, description="Generated section data (only when completed)")
    error: Optional[str] = Field(None, description="Error message (only when failed)")
    created_at: Optional[datetime] = Field(None, description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "507f1f77bcf86cd799439011",
                "status": "completed",
                "stock_id": "399834",
                "requested_sections": ["1", "2", "3"],
                "sections_data": [
                    {
                        "section_id": "1",
                        "section_name": "Company Information",
                        "content": "..."
                    }
                ],
                "created_at": "2025-10-31T10:30:00",
                "completed_at": "2025-10-31T10:30:12"
            }
        }
