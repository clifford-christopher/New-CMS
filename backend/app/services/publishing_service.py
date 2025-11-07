"""
Publishing Service
Story 5.2: Configuration Publishing with Confirmation

Service for publishing trigger configurations to production
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..models.published_config import (
    PublishedConfiguration,
    PublishRequest,
    PublishResponse,
    TestResultsSummary
)
from .audit_service import get_audit_service


class PublishingService:
    """
    Service for publishing trigger configurations

    Responsibilities:
    - Auto-increment version numbers per trigger
    - Deactivate old configurations
    - Save configuration snapshots with test metadata
    - Return published configuration details
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.published_configs = db.published_configs

    async def publish_configuration(
        self,
        trigger_id: str,
        publish_request: PublishRequest
    ) -> PublishResponse:
        """
        Publish a new configuration version for a trigger

        Args:
            trigger_id: Trigger identifier
            publish_request: Configuration and metadata to publish

        Returns:
            PublishResponse with success status and version info
        """
        try:
            # Step 1: Get next version number
            next_version = await self._get_next_version(trigger_id)

            # Get previous active version for audit log
            previous_config = await self.get_active_configuration(trigger_id)
            previous_version = previous_config.version if previous_config else None

            # Step 2: Deactivate all existing configurations for this trigger
            await self._deactivate_existing_configs(trigger_id)

            # Step 3: Create new published configuration
            published_config = PublishedConfiguration(
                trigger_id=trigger_id,
                version=next_version,
                apis=publish_request.apis,
                section_order=publish_request.section_order,
                prompts=publish_request.prompts,
                model_settings=publish_request.model_settings,
                test_results_summary=publish_request.test_results_summary,
                is_active=True,
                published_at=datetime.utcnow(),
                published_by=publish_request.published_by
            )

            # Step 4: Insert into database
            config_dict = published_config.model_dump()
            result = await self.published_configs.insert_one(config_dict)

            if not result.inserted_id:
                raise RuntimeError("Failed to insert published configuration")

            # Step 5: Log the publish action to audit log
            audit_service = get_audit_service(self.db)
            await audit_service.log_action(
                trigger_id=trigger_id,
                action="publish",
                performed_by=publish_request.published_by,
                version=next_version,
                previous_version=previous_version,
                notes=publish_request.notes,
                metadata={
                    "test_results_summary": {
                        pt: summary.model_dump()
                        for pt, summary in publish_request.test_results_summary.items()
                    },
                    "apis": publish_request.apis,
                    "model_settings": publish_request.model_settings
                },
                success=True
            )

            # Step 6: Return response
            return PublishResponse(
                success=True,
                message=f"Configuration published successfully as version {next_version}",
                trigger_id=trigger_id,
                version=next_version,
                published_at=published_config.published_at,
                is_active=True
            )

        except Exception as e:
            # Log failed publish attempt
            audit_service = get_audit_service(self.db)
            await audit_service.log_action(
                trigger_id=trigger_id,
                action="publish",
                performed_by=publish_request.published_by,
                notes=publish_request.notes,
                success=False,
                error_message=str(e)
            )
            raise

    async def _get_next_version(self, trigger_id: str) -> int:
        """
        Get the next version number for a trigger

        Args:
            trigger_id: Trigger identifier

        Returns:
            Next version number (1 if no previous versions)
        """
        # Find the highest version number for this trigger
        latest_config = await self.published_configs.find_one(
            {"trigger_id": trigger_id},
            sort=[("version", -1)]
        )

        if not latest_config:
            return 1

        return latest_config["version"] + 1

    async def _deactivate_existing_configs(self, trigger_id: str) -> None:
        """
        Mark all existing configurations for a trigger as inactive

        Args:
            trigger_id: Trigger identifier
        """
        await self.published_configs.update_many(
            {"trigger_id": trigger_id, "is_active": True},
            {"$set": {"is_active": False}}
        )

    async def get_active_configuration(
        self,
        trigger_id: str
    ) -> Optional[PublishedConfiguration]:
        """
        Get the active published configuration for a trigger

        Args:
            trigger_id: Trigger identifier

        Returns:
            Active PublishedConfiguration or None
        """
        config_dict = await self.published_configs.find_one({
            "trigger_id": trigger_id,
            "is_active": True
        })

        if not config_dict:
            return None

        return PublishedConfiguration(**config_dict)

    async def get_configuration_by_version(
        self,
        trigger_id: str,
        version: int
    ) -> Optional[PublishedConfiguration]:
        """
        Get a specific version of a published configuration

        Args:
            trigger_id: Trigger identifier
            version: Version number

        Returns:
            PublishedConfiguration or None
        """
        config_dict = await self.published_configs.find_one({
            "trigger_id": trigger_id,
            "version": version
        })

        if not config_dict:
            return None

        return PublishedConfiguration(**config_dict)

    async def get_all_versions(
        self,
        trigger_id: str,
        limit: int = 50
    ) -> List[PublishedConfiguration]:
        """
        Get all published versions for a trigger (newest first)

        Args:
            trigger_id: Trigger identifier
            limit: Maximum number of versions to return

        Returns:
            List of PublishedConfiguration objects
        """
        cursor = self.published_configs.find(
            {"trigger_id": trigger_id}
        ).sort("version", -1).limit(limit)

        configs = await cursor.to_list(length=limit)

        return [PublishedConfiguration(**config) for config in configs]

    async def rollback_to_version(
        self,
        trigger_id: str,
        target_version: int,
        published_by: str
    ) -> PublishResponse:
        """
        Rollback to a previous configuration version

        Creates a new version that's a copy of the target version

        Args:
            trigger_id: Trigger identifier
            target_version: Version to rollback to
            published_by: User ID performing rollback

        Returns:
            PublishResponse with new version info
        """
        try:
            # Get the target version
            target_config = await self.get_configuration_by_version(trigger_id, target_version)

            if not target_config:
                raise ValueError(f"Version {target_version} not found for trigger {trigger_id}")

            # Get current active version for audit log
            current_config = await self.get_active_configuration(trigger_id)
            current_version = current_config.version if current_config else None

            # Create publish request from target config
            publish_request = PublishRequest(
                apis=target_config.apis,
                section_order=target_config.section_order,
                prompts=target_config.prompts,
                model_settings=target_config.model_settings,
                test_results_summary=target_config.test_results_summary,
                published_by=published_by,
                notes=f"Rollback to version {target_version}"
            )

            # Publish as new version
            response = await self.publish_configuration(trigger_id, publish_request)
            response.message = f"Rolled back to version {target_version} (published as v{response.version})"

            # Log the rollback action
            audit_service = get_audit_service(self.db)
            await audit_service.log_action(
                trigger_id=trigger_id,
                action="rollback",
                performed_by=published_by,
                version=response.version,
                previous_version=current_version,
                notes=f"Rolled back to version {target_version}",
                metadata={
                    "target_version": target_version,
                    "new_version": response.version
                },
                success=True
            )

            return response

        except Exception as e:
            # Log failed rollback attempt
            audit_service = get_audit_service(self.db)
            await audit_service.log_action(
                trigger_id=trigger_id,
                action="rollback",
                performed_by=published_by,
                metadata={"target_version": target_version},
                success=False,
                error_message=str(e)
            )
            raise

    async def get_publish_stats(self, trigger_id: str) -> Dict[str, Any]:
        """
        Get publishing statistics for a trigger

        Args:
            trigger_id: Trigger identifier

        Returns:
            Dictionary with stats
        """
        versions = await self.get_all_versions(trigger_id, limit=1000)

        if not versions:
            return {
                "total_versions": 0,
                "active_version": None,
                "latest_version": None,
                "first_published": None,
                "last_published": None
            }

        active_config = next((v for v in versions if v.is_active), None)

        return {
            "total_versions": len(versions),
            "active_version": active_config.version if active_config else None,
            "latest_version": versions[0].version,
            "first_published": versions[-1].published_at,
            "last_published": versions[0].published_at,
            "publishers": list(set(v.published_by for v in versions))
        }


def get_publishing_service(db: AsyncIOMotorDatabase) -> PublishingService:
    """
    Factory function to get PublishingService instance

    Args:
        db: MongoDB database instance

    Returns:
        PublishingService instance
    """
    return PublishingService(db)
