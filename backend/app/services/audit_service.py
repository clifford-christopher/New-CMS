"""
Audit Service
Story 5.3: Audit Log for Publishing History

Service for logging and retrieving publishing audit trails
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.audit_log import (
    AuditLog,
    AuditAction,
    AuditLogFilter,
    AuditLogStats
)


class AuditService:
    """
    Service for managing audit logs

    Responsibilities:
    - Log publishing events
    - Query audit history with filters
    - Generate audit statistics
    - Support compliance and troubleshooting
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.audit_logs = db.audit_log

    async def log_action(
        self,
        trigger_id: str,
        action: str,
        performed_by: str,
        version: Optional[int] = None,
        previous_version: Optional[int] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """
        Log an audit action

        Args:
            trigger_id: Trigger identifier
            action: Action performed (publish, rollback, etc.)
            performed_by: User ID who performed the action
            version: Version number affected
            previous_version: Previous active version
            notes: User-provided notes
            metadata: Additional metadata
            success: Whether the action succeeded
            error_message: Error message if action failed

        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            trigger_id=trigger_id,
            action=action,
            performed_by=performed_by,
            timestamp=datetime.utcnow(),
            version=version,
            previous_version=previous_version,
            notes=notes,
            metadata=metadata or {},
            success=success,
            error_message=error_message
        )

        # Insert into database
        log_dict = audit_log.model_dump()
        await self.audit_logs.insert_one(log_dict)

        return audit_log

    async def get_audit_logs(
        self,
        filter_params: AuditLogFilter
    ) -> List[AuditLog]:
        """
        Get audit logs with filters

        Args:
            filter_params: Filter parameters

        Returns:
            List of AuditLog entries
        """
        # Build query
        query: Dict[str, Any] = {}

        if filter_params.trigger_id:
            query["trigger_id"] = filter_params.trigger_id

        if filter_params.action:
            query["action"] = filter_params.action

        if filter_params.performed_by:
            query["performed_by"] = filter_params.performed_by

        if filter_params.success_only is not None:
            query["success"] = filter_params.success_only

        # Date range filter
        if filter_params.start_date or filter_params.end_date:
            query["timestamp"] = {}
            if filter_params.start_date:
                query["timestamp"]["$gte"] = filter_params.start_date
            if filter_params.end_date:
                query["timestamp"]["$lte"] = filter_params.end_date

        # Execute query
        cursor = self.audit_logs.find(query).sort("timestamp", -1).skip(filter_params.skip).limit(filter_params.limit)

        logs = await cursor.to_list(length=filter_params.limit)

        return [AuditLog(**log) for log in logs]

    async def get_audit_log_by_id(self, log_id: str) -> Optional[AuditLog]:
        """
        Get a specific audit log by ID

        Args:
            log_id: Audit log ID

        Returns:
            AuditLog or None
        """
        from bson import ObjectId

        try:
            log_dict = await self.audit_logs.find_one({"_id": ObjectId(log_id)})
            if not log_dict:
                return None
            return AuditLog(**log_dict)
        except Exception:
            return None

    async def get_stats(self, trigger_id: str) -> AuditLogStats:
        """
        Get audit statistics for a trigger

        Args:
            trigger_id: Trigger identifier

        Returns:
            AuditLogStats with statistics
        """
        # Get all logs for trigger
        all_logs = await self.audit_logs.find({"trigger_id": trigger_id}).to_list(length=10000)

        if not all_logs:
            return AuditLogStats(
                total_publishes=0,
                total_rollbacks=0,
                total_actions=0,
                last_publish=None,
                unique_publishers=0,
                success_rate=0.0
            )

        # Calculate stats
        total_actions = len(all_logs)
        total_publishes = sum(1 for log in all_logs if log.get("action") == "publish")
        total_rollbacks = sum(1 for log in all_logs if log.get("action") == "rollback")
        successful_actions = sum(1 for log in all_logs if log.get("success", True))
        success_rate = (successful_actions / total_actions * 100) if total_actions > 0 else 0.0

        # Get last publish timestamp
        publish_logs = [log for log in all_logs if log.get("action") == "publish"]
        last_publish = None
        if publish_logs:
            last_publish = max(log.get("timestamp") for log in publish_logs)

        # Count unique publishers
        unique_publishers = len(set(log.get("performed_by") for log in all_logs if log.get("performed_by")))

        return AuditLogStats(
            total_publishes=total_publishes,
            total_rollbacks=total_rollbacks,
            total_actions=total_actions,
            last_publish=last_publish,
            unique_publishers=unique_publishers,
            success_rate=success_rate
        )

    async def get_recent_actions(
        self,
        trigger_id: Optional[str] = None,
        limit: int = 10
    ) -> List[AuditLog]:
        """
        Get recent audit actions

        Args:
            trigger_id: Optional trigger filter
            limit: Number of recent actions to return

        Returns:
            List of recent AuditLog entries
        """
        query = {"trigger_id": trigger_id} if trigger_id else {}

        cursor = self.audit_logs.find(query).sort("timestamp", -1).limit(limit)
        logs = await cursor.to_list(length=limit)

        return [AuditLog(**log) for log in logs]

    async def get_version_history(
        self,
        trigger_id: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Get version history for a trigger (publish and rollback actions only)

        Args:
            trigger_id: Trigger identifier
            limit: Maximum number of entries

        Returns:
            List of AuditLog entries for version changes
        """
        query = {
            "trigger_id": trigger_id,
            "action": {"$in": ["publish", "rollback"]}
        }

        cursor = self.audit_logs.find(query).sort("timestamp", -1).limit(limit)
        logs = await cursor.to_list(length=limit)

        return [AuditLog(**log) for log in logs]


def get_audit_service(db: AsyncIOMotorDatabase) -> AuditService:
    """
    Factory function to get AuditService instance

    Args:
        db: MongoDB database instance

    Returns:
        AuditService instance
    """
    return AuditService(db)
