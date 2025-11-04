"""
FastAPI router for trigger management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from ..database import get_database
from ..models.trigger_prompt_config import TriggerPromptConfig
import logging

# Available data APIs registry
AVAILABLE_APIS = [
    {
        "api_id": "earnings_api",
        "name": "Earnings Data API",
        "description": "Quarterly and annual earnings reports",
        "required": True,
        "category": "Financial"
    },
    {
        "api_id": "price_data_api",
        "name": "Price Data API",
        "description": "Historical stock price and volume data",
        "required": True,
        "category": "Market"
    },
    {
        "api_id": "balance_sheet_api",
        "name": "Balance Sheet API",
        "description": "Company balance sheet data",
        "required": False,
        "category": "Financial"
    },
    {
        "api_id": "cash_flow_api",
        "name": "Cash Flow API",
        "description": "Cash flow statements",
        "required": False,
        "category": "Financial"
    },
    {
        "api_id": "ratios_api",
        "name": "Financial Ratios API",
        "description": "Key financial ratios and metrics",
        "required": False,
        "category": "Analytics"
    },
    {
        "api_id": "shareholding_api",
        "name": "Shareholding Pattern API",
        "description": "Promoter and institutional holdings",
        "required": False,
        "category": "Ownership"
    },
    {
        "api_id": "technical_api",
        "name": "Technical Indicators API",
        "description": "Technical analysis indicators",
        "required": False,
        "category": "Technical"
    },
    {
        "api_id": "news_sentiment_api",
        "name": "News Sentiment API",
        "description": "News articles and sentiment scores",
        "required": False,
        "category": "Alternative"
    }
]

router = APIRouter(prefix="/api/triggers", tags=["triggers"])
logger = logging.getLogger(__name__)


@router.get("/")
async def get_triggers():
    """
    Get all trigger configurations from MongoDB trigger_prompts collection.

    Returns list of triggers with:
    - trigger_name: Trigger identifier
    - isActive: Whether News CMS Workflow is enabled
    - llm_config, data_config, prompts: Configuration details (if set)
    - version, timestamps: Metadata

    Returns:
        List[dict]: List of trigger configurations

    Raises:
        HTTPException: 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Query all triggers from trigger_prompts collection
        triggers_cursor = db.trigger_prompts.find({})
        triggers_list = await triggers_cursor.to_list(length=100)

        # Convert MongoDB documents to response format
        triggers = []
        for trigger_doc in triggers_list:
            try:
                # Parse with Pydantic for validation
                trigger = TriggerPromptConfig(**trigger_doc)

                # Convert to dict for response
                trigger_dict = {
                    "trigger_name": trigger.trigger_name,
                    "isActive": trigger.isActive,
                    "status": "configured" if trigger.isActive else "unconfigured",
                    "has_llm_config": trigger.llm_config is not None,
                    "has_data_config": trigger.data_config is not None,
                    "has_prompts": trigger.prompts is not None,
                    "version": trigger.version,
                    "updated_at": trigger.updated_at.isoformat(),
                    "published_at": trigger.published_at.isoformat() if trigger.published_at else None,
                    "published_by": trigger.published_by
                }
                triggers.append(trigger_dict)
            except Exception as e:
                logger.warning(f"Failed to parse trigger {trigger_doc.get('trigger_name', 'unknown')}: {e}")
                # Include raw trigger with basic info
                triggers.append({
                    "trigger_name": trigger_doc.get("trigger_name", "unknown"),
                    "isActive": trigger_doc.get("isActive", False),
                    "status": "unconfigured",
                    "has_llm_config": False,
                    "has_data_config": False,
                    "has_prompts": False,
                    "version": trigger_doc.get("version", 1),
                    "updated_at": None,
                    "published_at": None,
                    "published_by": None,
                    "error": "Failed to parse trigger configuration"
                })

        logger.info(f"Retrieved {len(triggers)} triggers from trigger_prompts collection")
        return triggers

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve triggers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve triggers: {str(e)}")


@router.get("/{trigger_name}")
async def get_trigger_detail(trigger_name: str):
    """
    Get detailed configuration for a specific trigger.

    Args:
        trigger_name: Trigger identifier (e.g., "earnings_result")

    Returns:
        dict: Full trigger configuration (raw document or parsed)

    Raises:
        HTTPException: 404 if not found, 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Find trigger by trigger_name
        trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not trigger_doc:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        # Try to parse with new schema, fall back to raw document
        try:
            trigger = TriggerPromptConfig(**trigger_doc)

            # Return parsed configuration
            return {
                "trigger_name": trigger.trigger_name,
                "isActive": trigger.isActive,
                "llm_config": trigger.llm_config.model_dump() if trigger.llm_config else None,
                "data_config": trigger.data_config.model_dump() if trigger.data_config else None,
                "prompts": trigger.prompts.model_dump() if trigger.prompts else None,
                "version": trigger.version,
                "created_at": trigger.created_at.isoformat(),
                "updated_at": trigger.updated_at.isoformat(),
                "published_at": trigger.published_at.isoformat() if trigger.published_at else None,
                "published_by": trigger.published_by,
                "schema": "new"
            }
        except Exception as parse_error:
            # Legacy format - return raw document with metadata
            logger.warning(f"Trigger '{trigger_name}' uses legacy schema: {parse_error}")

            # Remove MongoDB _id for JSON serialization
            trigger_doc.pop("_id", None)

            return {
                "trigger_name": trigger_name,
                "isActive": False,
                "schema": "legacy",
                "legacy_data": trigger_doc,
                "message": "This trigger uses the legacy schema. It will need to be reconfigured using the News CMS Workflow interface."
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trigger: {str(e)}")


@router.get("/{trigger_name}/config")
async def get_trigger_config(trigger_name: str):
    """
    Get trigger configuration including data API configuration.

    Args:
        trigger_name: Trigger identifier

    Returns:
        dict: Trigger configuration with data_config.apis list

    Raises:
        HTTPException: 404 if not found, 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Find trigger by trigger_name
        trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not trigger_doc:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        # Try to parse with Pydantic, but fall back to raw document access if it fails
        try:
            trigger = TriggerPromptConfig(**trigger_doc)

            # Extract data_config.apis or return empty list
            apis = []
            if trigger.data_config and trigger.data_config.apis:
                apis = trigger.data_config.apis

            # Extract prompts if available
            prompts = None
            if trigger.prompts:
                prompts = trigger.prompts.model_dump()

            return {
                "trigger_name": trigger.trigger_name,
                "isActive": trigger.isActive,
                "data_config": {
                    "apis": apis,
                    "has_config": trigger.data_config is not None
                },
                "prompts": prompts,
                "version": trigger.version,
                "updated_at": trigger.updated_at.isoformat()
            }
        except Exception as parse_error:
            logger.warning(f"Trigger '{trigger_name}' failed Pydantic validation, falling back to raw document: {parse_error}")

            # Fallback: Return raw document with prompts field
            # This handles legacy formats that don't match the Pydantic model
            trigger_doc.pop("_id", None)

            return {
                "trigger_name": trigger_doc.get("trigger_name", trigger_name),
                "isActive": trigger_doc.get("isActive", False),
                "data_config": {
                    "apis": trigger_doc.get("data_config", {}).get("apis", []) if isinstance(trigger_doc.get("data_config"), dict) else [],
                    "has_config": "data_config" in trigger_doc
                },
                "prompts": trigger_doc.get("prompts"),  # Return prompts as-is (legacy or new format)
                "version": trigger_doc.get("version", 1),
                "updated_at": trigger_doc.get("updated_at", datetime.utcnow()).isoformat() if hasattr(trigger_doc.get("updated_at"), "isoformat") else str(trigger_doc.get("updated_at", ""))
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve config for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trigger config: {str(e)}")


@router.post("/{trigger_name}/config/apis")
async def add_api_to_trigger(trigger_name: str, api_data: dict):
    """
    Add a data API to trigger's configuration.

    Args:
        trigger_name: Trigger identifier
        api_data: API configuration (e.g., {"api_id": "earnings_api", "name": "Earnings API"})

    Returns:
        dict: Updated APIs list

    Raises:
        HTTPException: 400 if duplicate, 404 if trigger not found, 503 if database not connected
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Find trigger
        trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not trigger_doc:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        # Get current APIs list
        current_apis = []
        if "data_config" in trigger_doc and trigger_doc["data_config"] and "apis" in trigger_doc["data_config"]:
            current_apis = trigger_doc["data_config"]["apis"]

        # Check for duplicates
        api_id = api_data.get("api_id")
        if any(api.get("api_id") == api_id for api in current_apis):
            raise HTTPException(status_code=400, detail=f"API '{api_id}' already configured for this trigger")

        # Add new API
        current_apis.append(api_data)

        # Update MongoDB
        update_result = await db.trigger_prompts.update_one(
            {"trigger_name": trigger_name},
            {
                "$set": {
                    "data_config.apis": current_apis,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if update_result.modified_count == 0:
            logger.warning(f"No document modified when adding API to trigger '{trigger_name}'")

        logger.info(f"Added API '{api_id}' to trigger '{trigger_name}'")

        return {
            "message": f"API '{api_id}' added successfully",
            "apis": current_apis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add API to trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add API: {str(e)}")


@router.delete("/{trigger_name}/config/apis/{api_id}")
async def remove_api_from_trigger(trigger_name: str, api_id: str):
    """
    Remove a data API from trigger's configuration.

    Args:
        trigger_name: Trigger identifier
        api_id: API identifier to remove

    Returns:
        dict: Updated APIs list

    Raises:
        HTTPException: 400 if required API, 404 if not found, 503 if database not connected
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Find trigger
        trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not trigger_doc:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        # Get current APIs list
        current_apis = []
        if "data_config" in trigger_doc and trigger_doc["data_config"] and "apis" in trigger_doc["data_config"]:
            current_apis = trigger_doc["data_config"]["apis"]

        # Find and remove API
        api_to_remove = None
        updated_apis = []
        for api in current_apis:
            if api.get("api_id") == api_id:
                api_to_remove = api
            else:
                updated_apis.append(api)

        if not api_to_remove:
            raise HTTPException(status_code=404, detail=f"API '{api_id}' not found in trigger configuration")

        # Check if API is required (basic validation - can be expanded)
        if api_to_remove.get("required", False):
            raise HTTPException(status_code=400, detail=f"Cannot remove required API '{api_id}'")

        # Update MongoDB
        update_result = await db.trigger_prompts.update_one(
            {"trigger_name": trigger_name},
            {
                "$set": {
                    "data_config.apis": updated_apis,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if update_result.modified_count == 0:
            logger.warning(f"No document modified when removing API from trigger '{trigger_name}'")

        logger.info(f"Removed API '{api_id}' from trigger '{trigger_name}'")

        return {
            "message": f"API '{api_id}' removed successfully",
            "apis": updated_apis
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove API from trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove API: {str(e)}")


@router.get("/available-apis")
async def get_available_apis():
    """
    Get list of all available data APIs that can be configured.

    Returns:
        List[dict]: List of available API configurations
    """
    return {
        "apis": AVAILABLE_APIS,
        "total": len(AVAILABLE_APIS)
    }


@router.post("/{trigger_name}/config/prompts")
async def update_prompts(trigger_name: str, prompts_data: dict):
    """
    Update prompt templates for all prompt types (paid, unpaid, crawler).

    Args:
        trigger_name: Trigger identifier
        prompts_data: Prompts object with paid, unpaid, crawler templates
                     Example: {"prompts": {"paid": {"template": "..."}, "unpaid": {"template": "..."}, "crawler": {"template": "..."}}}

    Returns:
        dict: Success status and updated configuration

    Raises:
        HTTPException: 400 if invalid prompt type, 404 if trigger not found, 503 if database not connected
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Find trigger
        trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not trigger_doc:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        # Extract prompts from request
        prompts = prompts_data.get("prompts", {})

        # Validate that prompt types are valid
        valid_types = {"paid", "unpaid", "crawler"}
        for prompt_type in prompts.keys():
            if prompt_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid prompt type: {prompt_type}. Must be one of: paid, unpaid, crawler"
                )

        # Build prompts update with metadata
        now = datetime.utcnow()
        prompts_update = {}

        for prompt_type, prompt_data in prompts.items():
            template = prompt_data.get("template", "")

            # Get existing prompt config or initialize
            existing_prompts = trigger_doc.get("prompts", {})
            existing_prompt = existing_prompts.get(prompt_type, {})
            version_history = existing_prompt.get("version_history", [])

            # Add current version to history (keep last 10)
            if existing_prompt.get("template"):
                version_history.append({
                    "template": existing_prompt["template"],
                    "timestamp": existing_prompt.get("last_saved", now),
                    "user_id": "current_user"  # TODO: Get from auth context
                })
                version_history = version_history[-10:]  # Keep last 10 versions

            prompts_update[f"prompts.{prompt_type}"] = {
                "template": template,
                "last_saved": now,
                "version_history": version_history,
                "character_count": len(template),
                "word_count": len(template.split()) if template else 0
            }

        # Update MongoDB
        update_result = await db.trigger_prompts.update_one(
            {"trigger_name": trigger_name},
            {
                "$set": {
                    **prompts_update,
                    "updated_at": now
                }
            }
        )

        if update_result.modified_count == 0:
            logger.warning(f"No document modified when updating prompts for trigger '{trigger_name}'")

        # Fetch updated document
        updated_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})
        updated_doc.pop("_id", None)

        logger.info(f"Updated prompts for trigger '{trigger_name}'")

        return {
            "success": True,
            "message": "Prompts updated successfully",
            "configuration": updated_doc
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update prompts for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update prompts: {str(e)}")
