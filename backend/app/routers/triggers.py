"""
FastAPI router for trigger management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from ..database import get_database
from ..models.trigger_prompt_config import TriggerPromptConfig
from ..models.trigger_prompt_draft import TriggerPromptDraft, PromptDraftResponse
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

    **Prompt Loading Strategy:**
    1. Check trigger_prompt_drafts for latest draft (SINGLE document with all prompt types)
    2. If no drafts exist, fallback to prompts in trigger_prompts (published versions)
    3. This allows users to see their latest changes even if not yet published

    Args:
        trigger_name: Trigger identifier

    Returns:
        dict: Trigger configuration with data_config.apis list and prompts (drafts or published)

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

        # Load latest draft (SINGLE document containing all prompt types)
        prompts = {}
        latest_draft = await db.trigger_prompt_drafts.find_one(
            {"trigger_name": trigger_name},
            sort=[("saved_at", -1)]  # Most recent first
        )

        if latest_draft:
            # Extract prompts from the single draft document
            draft_prompts = latest_draft.get("prompts", {})
            for prompt_type in ["paid", "unpaid", "crawler"]:
                if prompt_type in draft_prompts:
                    prompt_data = draft_prompts[prompt_type]
                    prompts[prompt_type] = {
                        "template": prompt_data.get("template", ""),
                        "last_saved": latest_draft.get("saved_at"),
                        "version": latest_draft.get("version"),
                        "is_draft": True
                    }
                elif prompt_type in (trigger_doc.get("prompts", {}) or {}):
                    # Fallback to published version from trigger_prompts
                    published_prompt = trigger_doc["prompts"][prompt_type]
                    prompts[prompt_type] = {
                        "template": published_prompt if isinstance(published_prompt, str) else published_prompt.get("template", published_prompt.get("article", "")),
                        "last_saved": trigger_doc.get("updated_at"),
                        "version": None,
                        "is_draft": False
                    }
        else:
            # No drafts exist, use published versions from trigger_prompts
            for prompt_type in ["paid", "unpaid", "crawler"]:
                if prompt_type in (trigger_doc.get("prompts", {}) or {}):
                    published_prompt = trigger_doc["prompts"][prompt_type]
                    prompts[prompt_type] = {
                        "template": published_prompt if isinstance(published_prompt, str) else published_prompt.get("template", published_prompt.get("article", "")),
                        "last_saved": trigger_doc.get("updated_at"),
                        "version": None,
                        "is_draft": False
                    }

        # Extract data_config.apis or return empty list
        data_config_apis = []
        if "data_config" in trigger_doc and isinstance(trigger_doc["data_config"], dict):
            data_config_apis = trigger_doc["data_config"].get("apis", [])

        trigger_doc.pop("_id", None)

        return {
            "trigger_name": trigger_doc.get("trigger_name", trigger_name),
            "isActive": trigger_doc.get("isActive", False),
            "data_config": {
                "apis": data_config_apis,
                "has_config": "data_config" in trigger_doc
            },
            "prompts": prompts,  # Merged prompts (drafts take priority)
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


@router.post("/{trigger_name}/config/prompts", response_model=PromptDraftResponse)
async def save_prompt_drafts(trigger_name: str, prompts_data: dict):
    """
    Save prompt drafts to trigger_prompt_drafts collection (does NOT modify trigger_prompts).

    Creates a SINGLE document containing all prompt types (paid, unpaid, crawler) for this trigger.
    Each save creates a new version, preserving full history.

    Args:
        trigger_name: Trigger identifier
        prompts_data: Prompts object with paid, unpaid, crawler templates
                     Example: {"prompts": {"paid": {"template": "..."}, "unpaid": {"template": "..."}, "crawler": {"template": "..."}}}

    Returns:
        PromptDraftResponse: Success status and created draft document

    Raises:
        HTTPException: 400 if invalid prompt type, 404 if trigger not found, 503 if database not connected
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Verify trigger exists in trigger_prompts collection
        trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not trigger_doc:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        # Extract prompts from request
        prompts_input = prompts_data.get("prompts", {})

        # Validate that prompt types are valid
        valid_types = {"paid", "unpaid", "crawler"}
        for prompt_type in prompts_input.keys():
            if prompt_type not in valid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid prompt type: {prompt_type}. Must be one of: paid, unpaid, crawler"
                )

        # Build prompts object for the draft
        now = datetime.utcnow()
        prompts_obj = {}

        for prompt_type in valid_types:
            if prompt_type in prompts_input:
                template = prompts_input[prompt_type].get("template", "")

                if template.strip():  # Only include non-empty prompts
                    prompts_obj[prompt_type] = {
                        "template": template,
                        "character_count": len(template),
                        "word_count": len(template.split()) if template else 0
                    }

        if not prompts_obj:
            raise HTTPException(status_code=400, detail="No valid prompts provided")

        # Get latest version number for this trigger
        latest_draft = await db.trigger_prompt_drafts.find_one(
            {"trigger_name": trigger_name},
            sort=[("version", -1)]
        )
        next_version = (latest_draft.get("version", 0) + 1) if latest_draft else 1

        # Create single draft document with all prompts
        draft = TriggerPromptDraft(
            trigger_name=trigger_name,
            prompts=prompts_obj,
            saved_by="system",  # TODO: Get from auth context
            saved_at=now,
            is_draft=True,
            version=next_version
        )

        # Insert into trigger_prompt_drafts collection
        draft_dict = draft.model_dump()
        result = await db.trigger_prompt_drafts.insert_one(draft_dict)

        draft_dict["_id"] = str(result.inserted_id)

        logger.info(f"Created draft for trigger '{trigger_name}' (version {next_version}) with {len(prompts_obj)} prompt(s)")

        return PromptDraftResponse(
            success=True,
            message=f"Saved prompt draft successfully (version {next_version})",
            draft=draft_dict,
            trigger_name=trigger_name,
            version=next_version
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save prompt drafts for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update prompts: {str(e)}")
