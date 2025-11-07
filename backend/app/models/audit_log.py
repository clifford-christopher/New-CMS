"""
Audit Log Model
Story 5.3: Audit Log for Publishing History

MongoDB schema for storing audit logs of publishing events
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AuditAction(str, Enum):
    """Types of audit actions"""
    PUBLISH = "publish"
    ROLLBACK = "rollback"
    DEACTIVATE = "deactivate"
    UPDATE = "update"
    CREATED = "created"  # Legacy action
    PROMPT_EDITED = "prompt_edited"  # Legacy action


class AuditLog(BaseModel):
    """
    Audit log entry for tracking publishing and configuration changes

    Captures:
    - Who made the change
    - What was changed
    - When it happened
    - Why it was changed (notes)
    - What the result was
    """

    # Identification
    trigger_id: str = Field(..., description="Trigger identifier")
    action: str = Field(..., description="Type of action performed")  # Using str to support legacy and new actions

    # Actor and timing
    performed_by: str = Field(..., description="User ID who performed the action")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the action occurred")

    # Details
    version: Optional[int] = Field(None, description="Version number affected (if applicable)")
    previous_version: Optional[int] = Field(None, description="Previous active version (for rollbacks)")
    notes: Optional[str] = Field(None, description="User-provided notes or reason for change")

    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (e.g., test results, config changes)"
    )

    # Result
    success: bool = Field(True, description="Whether the action succeeded")
    error_message: Optional[str] = Field(None, description="Error message if action failed")

    class Config:
        json_schema_extra = {
            "example": {
                "trigger_id": "earnings",
                "action": "publish",
                "performed_by": "user123",
                "timestamp": "2025-11-06T14:30:00Z",
                "version": 5,
                "previous_version": 4,
                "notes": "Updated prompts for better accuracy",
                "metadata": {
                    "test_results_summary": {
                        "paid": {
                            "models_tested": ["gpt-4o", "claude-3.5-sonnet"],
                            "avg_cost": 0.42,
                            "avg_latency": 8.5,
                            "total_tests": 2
                        }
                    },
                    "apis_changed": True,
                    "prompts_changed": True
                },
                "success": True
            }
        }


class AuditLogFilter(BaseModel):
    """Filter parameters for querying audit logs"""
    trigger_id: Optional[str] = None
    action: Optional[str] = None
    performed_by: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    success_only: Optional[bool] = None
    limit: int = Field(default=50, le=500, description="Maximum number of results")
    skip: int = Field(default=0, ge=0, description="Number of results to skip")


class AuditLogStats(BaseModel):
    """Statistics about audit logs for a trigger"""
    total_publishes: int
    total_rollbacks: int
    total_actions: int
    last_publish: Optional[datetime]
    unique_publishers: int
    success_rate: float  # Percentage of successful actions
