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


@router.get("/{trigger_name}/config/prompts/versions")
async def get_prompt_versions(trigger_name: str):
    """
    Get list of all saved prompt versions for a trigger.

    Returns version metadata including version number, timestamp, and author
    for all saved drafts of the specified trigger.

    Args:
        trigger_name: Trigger identifier

    Returns:
        dict: Contains 'versions' array and 'total' count

    Raises:
        HTTPException: 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Find all drafts for this trigger, sorted by version (newest first)
        drafts_cursor = db.trigger_prompt_drafts.find(
            {"trigger_name": trigger_name}
        ).sort("version", -1)

        drafts = await drafts_cursor.to_list(length=100)

        # Extract version metadata
        versions = [
            {
                "version": d["version"],
                "saved_at": d["saved_at"].isoformat() if hasattr(d.get("saved_at"), "isoformat") else str(d.get("saved_at", "")),
                "saved_by": d.get("saved_by", "unknown"),
                "is_draft": d.get("is_draft", True),
                "prompt_types": list(d.get("prompts", {}).keys())
            }
            for d in drafts
        ]

        return {
            "versions": versions,
            "total": len(versions),
            "trigger_name": trigger_name
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve prompt versions for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve versions: {str(e)}")


@router.get("/{trigger_name}/config/prompts/version/{version_number}")
async def get_prompt_version(trigger_name: str, version_number: int):
    """
    Get specific version of prompts for preview.

    Retrieves the complete prompt data for a specific version number,
    allowing users to preview or restore historical versions.

    Args:
        trigger_name: Trigger identifier
        version_number: Version number to retrieve

    Returns:
        dict: Complete prompt data for the specified version including all prompt types

    Raises:
        HTTPException: 404 if version not found, 503 if database not connected, 500 on other errors
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Find specific version
        draft = await db.trigger_prompt_drafts.find_one({
            "trigger_name": trigger_name,
            "version": version_number
        })

        if not draft:
            raise HTTPException(
                status_code=404,
                detail=f"Version {version_number} not found for trigger '{trigger_name}'"
            )

        # Remove MongoDB _id field
        draft.pop("_id", None)

        # Format the response similar to get_trigger_config
        prompts = {}
        draft_prompts = draft.get("prompts", {})

        for prompt_type in ["paid", "unpaid", "crawler"]:
            if prompt_type in draft_prompts:
                prompt_data = draft_prompts[prompt_type]
                prompts[prompt_type] = {
                    "template": prompt_data.get("template", ""),
                    "character_count": prompt_data.get("character_count", 0),
                    "word_count": prompt_data.get("word_count", 0),
                    "last_saved": draft.get("saved_at"),
                    "version": draft.get("version"),
                    "is_draft": True
                }

        return {
            "trigger_name": trigger_name,
            "version": draft.get("version"),
            "saved_at": draft.get("saved_at").isoformat() if hasattr(draft.get("saved_at"), "isoformat") else str(draft.get("saved_at", "")),
            "saved_by": draft.get("saved_by", "unknown"),
            "prompts": prompts,
            "is_draft": draft.get("is_draft", True)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve version {version_number} for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve version: {str(e)}")


@router.post("/{trigger_name}/config/models")
async def update_model_config(trigger_name: str, model_config: dict):
    """
    Update model selection configuration for trigger (saves to DRAFT).

    This endpoint stores the selected LLM models, temperature, and max_tokens in the
    draft collection. Model selection is shared across all prompt types
    (paid, unpaid, crawler) for this trigger.

    NOTE: This saves to trigger_prompt_drafts, not trigger_prompts.
    Use the publish endpoint to make changes live.

    Args:
        trigger_name: Trigger identifier
        model_config: Configuration object with:
            - selected_models: List of model IDs (e.g., ["gpt-4o", "claude-sonnet-4-5"])
            - temperature: Generation temperature (0.0-1.0)
            - max_tokens: Maximum tokens to generate (50-4000)

    Example:
        ```json
        {
            "selected_models": ["gpt-4o", "claude-sonnet-4-5", "gemini-2.0-flash"],
            "temperature": 0.7,
            "max_tokens": 500
        }
        ```

    Returns:
        dict: Updated draft configuration and success message

    Raises:
        HTTPException: 400 if validation fails, 503 if database not connected
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Extract and validate configuration
        selected_models = model_config.get("selected_models", [])
        temperature = model_config.get("temperature", 0.7)
        max_tokens = model_config.get("max_tokens", 500)

        # Validation: At least one model required
        if not selected_models or not isinstance(selected_models, list) or len(selected_models) == 0:
            raise HTTPException(status_code=400, detail="At least one model must be selected")

        # Validation: Temperature range (0.0 - 1.0)
        if not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 1.0:
            raise HTTPException(status_code=400, detail="Temperature must be between 0.0 and 1.0")

        # Validation: Max tokens range (50 - 4000)
        if not isinstance(max_tokens, int) or max_tokens < 50 or max_tokens > 4000:
            raise HTTPException(status_code=400, detail="Max tokens must be between 50 and 4000")

        # Validate model IDs against available models
        from ..llm_providers import ProviderRegistry
        available_models = ProviderRegistry.list_available_models()
        available_model_ids = {model["model_id"] for model in available_models}

        invalid_models = [model_id for model_id in selected_models if model_id not in available_model_ids]
        if invalid_models:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model IDs: {', '.join(invalid_models)}. Use /api/news/models to see available models."
            )

        # Build model_config_data object
        model_config_data = {
            "selected_models": selected_models,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "updated_at": datetime.utcnow()
        }

        # Find latest draft for this trigger
        latest_draft = await db.trigger_prompt_drafts.find_one(
            {"trigger_name": trigger_name},
            sort=[("version", -1)]
        )

        if latest_draft:
            # Update existing draft
            update_result = await db.trigger_prompt_drafts.update_one(
                {"_id": latest_draft["_id"]},
                {
                    "$set": {
                        "model_config_data": model_config_data,
                        "saved_at": datetime.utcnow()
                    }
                }
            )
            version = latest_draft.get("version", 1)
            logger.info(f"Updated draft version {version} with model config for trigger '{trigger_name}'")
        else:
            # No draft exists, create a new one with just model config
            # (prompts will be added when they are configured)
            new_draft = {
                "trigger_name": trigger_name,
                "prompts": {},  # Empty prompts, will be filled later
                "model_config_data": model_config_data,
                "data_config": None,
                "saved_by": "system",
                "saved_at": datetime.utcnow(),
                "is_draft": True,
                "version": 1,
                "session_id": None
            }
            result = await db.trigger_prompt_drafts.insert_one(new_draft)
            version = 1
            logger.info(f"Created new draft (version 1) with model config for trigger '{trigger_name}'")

        logger.info(
            f"Saved model config to draft for trigger '{trigger_name}': "
            f"{len(selected_models)} model(s), temp={temperature}, max_tokens={max_tokens}"
        )

        return {
            "success": True,
            "message": f"Model configuration saved to draft for '{trigger_name}'",
            "model_config": model_config_data,
            "models_count": len(selected_models),
            "is_draft": True,
            "version": version
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model config for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update model configuration: {str(e)}")


@router.get("/{trigger_name}/config/models")
async def get_model_config(trigger_name: str):
    """
    Get current model configuration for a trigger.

    Retrieves the model selection from the LATEST DRAFT first, then falls back
    to published configuration if no draft exists.

    Args:
        trigger_name: Trigger identifier

    Returns:
        dict: Current model configuration or default values if not set

    Raises:
        HTTPException: 503 if database not connected
    """
    try:
        db = get_database()

        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Try to find latest draft first (preferred)
        draft_doc = await db.trigger_prompt_drafts.find_one(
            {"trigger_name": trigger_name},
            sort=[("version", -1)]
        )

        model_config_data = None
        is_draft = False

        if draft_doc and draft_doc.get("model_config_data"):
            # Use draft configuration
            model_config_data = draft_doc.get("model_config_data", {})
            is_draft = True
        else:
            # Fall back to published configuration
            trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})
            if trigger_doc:
                model_config_data = trigger_doc.get("model_config_data", {})
                is_draft = False

        # Return defaults if no configuration found
        if not model_config_data:
            return {
                "trigger_name": trigger_name,
                "model_config": {
                    "selected_models": [],
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "updated_at": None
                },
                "is_configured": False,
                "is_draft": False,
                "message": "No model configuration set. Use POST to configure models."
            }

        return {
            "trigger_name": trigger_name,
            "model_config": {
                "selected_models": model_config_data.get("selected_models", []),
                "temperature": model_config_data.get("temperature", 0.7),
                "max_tokens": model_config_data.get("max_tokens", 500),
                "updated_at": model_config_data.get("updated_at").isoformat() if model_config_data.get("updated_at") else None
            },
            "is_configured": True,
            "is_draft": is_draft,
            "models_count": len(model_config_data.get("selected_models", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve model config for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve model configuration: {str(e)}")


@router.post("/{trigger_name}/drafts")
async def save_complete_draft(trigger_name: str, draft_data: dict):
    """
    Save complete trigger configuration to drafts (unified endpoint).

    This endpoint saves ALL configuration atomically:
    - Prompts (paid, unpaid, crawler)
    - Model configuration (selected_models, temperature, max_tokens)
    - Data configuration (data_mode, selected_sections, section_order)

    Expected payload:
    {
        "prompts": {
            "paid": {"template": "...", "character_count": 0, "word_count": 0},
            "unpaid": {...},
            "crawler": {...}
        },
        "model_config": {
            "selected_models": ["gpt-4o", "claude-sonnet-4-5"],
            "temperature": 0.7,
            "max_tokens": 500
        },
        "data_config": {
            "data_mode": "NEW",
            "selected_sections": [1, 2, 3],
            "section_order": [2, 3, 1]
        },
        "saved_by": "user123"  // optional
    }

    This saves to trigger_prompt_drafts. Use /publish endpoint to make changes live.
    """
    try:
        # Extract components from payload
        prompts_data = draft_data.get("prompts", {})
        model_config = draft_data.get("model_config", {})
        data_config = draft_data.get("data_config", {})
        saved_by = draft_data.get("saved_by", "system")

        # Validate trigger exists
        trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})
        if not trigger_doc:
            raise HTTPException(status_code=404, detail=f"Trigger '{trigger_name}' not found")

        # Find latest draft for this trigger
        latest_draft = await db.trigger_prompt_drafts.find_one(
            {"trigger_name": trigger_name},
            sort=[("version", -1)]
        )

        # Prepare complete draft document
        draft_document = {
            "trigger_name": trigger_name,
            "prompts": prompts_data,
            "model_config_data": model_config if model_config else None,
            "data_config": data_config if data_config else None,
            "saved_by": saved_by,
            "saved_at": datetime.utcnow(),
            "is_draft": True,
            "session_id": draft_data.get("session_id", None)
        }

        if latest_draft:
            # Update existing draft (in place - same version)
            update_result = await db.trigger_prompt_drafts.update_one(
                {"_id": latest_draft["_id"]},
                {"$set": draft_document}
            )
            version = latest_draft.get("version", 1)
            logger.info(f"Updated complete draft version {version} for trigger '{trigger_name}'")
        else:
            # Create new draft (version 1)
            draft_document["version"] = 1
            result = await db.trigger_prompt_drafts.insert_one(draft_document)
            version = 1
            logger.info(f"Created new complete draft (version 1) for trigger '{trigger_name}'")

        return {
            "success": True,
            "message": f"Complete draft saved for '{trigger_name}'",
            "trigger_name": trigger_name,
            "version": version,
            "is_draft": True,
            "saved_at": draft_document["saved_at"].isoformat(),
            "components_saved": {
                "prompts": len(prompts_data),
                "model_config": bool(model_config),
                "data_config": bool(data_config)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save complete draft for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save draft: {str(e)}")


@router.post("/{trigger_name}/publish")
async def publish_draft(trigger_name: str, publish_data: dict = None):
    """
    Publish a draft configuration to production.

    This endpoint copies the latest draft from trigger_prompt_drafts to trigger_prompts,
    making the configuration live. This includes:
    - Prompts (paid, unpaid, crawler)
    - Model configuration (selected_models, temperature, max_tokens)
    - Data configuration (data_mode, selected_sections, section_order)

    Optional payload:
    {
        "published_by": "user123"  // optional, who published
    }

    After publishing, the draft remains in trigger_prompt_drafts for history tracking.
    """
    try:
        # Find latest draft for this trigger
        latest_draft = await db.trigger_prompt_drafts.find_one(
            {"trigger_name": trigger_name},
            sort=[("version", -1)]
        )

        if not latest_draft:
            raise HTTPException(
                status_code=404,
                detail=f"No draft found for trigger '{trigger_name}'. Save a draft first before publishing."
            )

        # Extract published_by from payload if provided
        published_by = "system"
        if publish_data and isinstance(publish_data, dict):
            published_by = publish_data.get("published_by", "system")

        # Check if trigger exists in production
        existing_trigger = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not existing_trigger:
            raise HTTPException(
                status_code=404,
                detail=f"Trigger '{trigger_name}' not found in trigger_prompts collection"
            )

        # Prepare published document (copy from draft)
        published_document = {
            "trigger_name": trigger_name,
            "prompts": latest_draft.get("prompts", {}),
            "model_config_data": latest_draft.get("model_config_data"),
            "data_config": latest_draft.get("data_config"),
            "published_by": published_by,
            "published_at": datetime.utcnow(),
            "is_draft": False,
            "draft_version_published": latest_draft.get("version", 1)
        }

        # Update the trigger_prompts collection
        update_result = await db.trigger_prompts.update_one(
            {"trigger_name": trigger_name},
            {"$set": published_document}
        )

        if update_result.modified_count == 0:
            logger.warning(f"No changes made when publishing draft for trigger '{trigger_name}'")

        logger.info(f"Published draft version {latest_draft.get('version', 1)} for trigger '{trigger_name}'")

        # Optionally increment draft version for next draft
        # This creates a clean slate for the next round of edits
        await db.trigger_prompt_drafts.update_one(
            {"_id": latest_draft["_id"]},
            {"$inc": {"version": 1}}
        )

        return {
            "success": True,
            "message": f"Draft published successfully for '{trigger_name}'",
            "trigger_name": trigger_name,
            "published_at": published_document["published_at"].isoformat(),
            "draft_version_published": latest_draft.get("version", 1),
            "published_by": published_by,
            "components_published": {
                "prompts": len(latest_draft.get("prompts", {})),
                "model_config": bool(latest_draft.get("model_config_data")),
                "data_config": bool(latest_draft.get("data_config"))
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish draft for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to publish draft: {str(e)}")


@router.get("/{trigger_name}/drafts/latest")
async def get_latest_draft(trigger_name: str):
    """
    Get the latest draft configuration for a trigger.

    Returns the complete draft including:
    - Prompts (paid, unpaid, crawler)
    - Model configuration
    - Data configuration
    - Version and metadata

    Used by frontend to load existing draft when page mounts.
    """
    try:
        # Find latest draft for this trigger
        latest_draft = await db.trigger_prompt_drafts.find_one(
            {"trigger_name": trigger_name},
            sort=[("version", -1)]
        )

        if not latest_draft:
            # No draft exists - return empty structure
            return {
                "success": True,
                "has_draft": False,
                "trigger_name": trigger_name,
                "message": "No draft found"
            }

        # Convert ObjectId to string for JSON serialization
        latest_draft["_id"] = str(latest_draft["_id"])

        # Convert datetime to ISO string
        if "saved_at" in latest_draft and latest_draft["saved_at"]:
            latest_draft["saved_at"] = latest_draft["saved_at"].isoformat()

        return {
            "success": True,
            "has_draft": True,
            "trigger_name": trigger_name,
            "draft": latest_draft,
            "version": latest_draft.get("version", 1),
            "is_draft": latest_draft.get("is_draft", True),
            "saved_at": latest_draft.get("saved_at")
        }

    except Exception as e:
        logger.error(f"Failed to retrieve latest draft for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve draft: {str(e)}")
