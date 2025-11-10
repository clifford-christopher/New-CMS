"""
FastAPI router for trigger management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
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


def apply_variant_strategy_mapping(prompts_data: dict, variant_strategy: str = "all_same") -> dict:
    """
    Apply variant strategy mapping to prompts.

    Takes raw prompt data and applies replication rules based on the variant strategy:
    - all_same: Use paid prompt for all types (1 API call)
    - all_unique: Use separate prompts for each type (3 API calls)
    - paid_unique: Unique paid, shared unpaid/crawler (2 API calls)
    - unpaid_unique: Unique unpaid, shared paid/crawler (2 API calls)
    - crawler_unique: Unique crawler, shared paid/unpaid (2 API calls)

    Args:
        prompts_data: Dictionary with prompt types as keys, each containing "template" field
        variant_strategy: Strategy to apply

    Returns:
        Dictionary with prompts replicated according to strategy, each with template/character_count/word_count
    """
    valid_types = ["paid", "unpaid", "crawler"]

    # Extract filled prompts (prompts with non-empty templates)
    filled_prompts = {}
    for prompt_type in valid_types:
        if prompt_type in prompts_data:
            template = prompts_data[prompt_type].get("template", "").strip()
            if template:
                filled_prompts[prompt_type] = template

    # Apply variant strategy mapping
    prompts_obj = {}

    if variant_strategy == "all_same":
        # All types use the paid prompt - save all 3 with same content
        if "paid" in filled_prompts:
            template = filled_prompts["paid"]
            for prompt_type in valid_types:
                prompts_obj[prompt_type] = {
                    "template": template,
                    "character_count": len(template),
                    "word_count": len(template.split())
                }
    elif variant_strategy == "all_unique":
        # Each type uses its own prompt - save only what's filled
        for prompt_type in valid_types:
            if prompt_type in filled_prompts:
                template = filled_prompts[prompt_type]
                prompts_obj[prompt_type] = {
                    "template": template,
                    "character_count": len(template),
                    "word_count": len(template.split())
                }
    elif variant_strategy == "paid_unique":
        # Paid is unique, unpaid/crawler share
        if "paid" in filled_prompts:
            template = filled_prompts["paid"]
            prompts_obj["paid"] = {
                "template": template,
                "character_count": len(template),
                "word_count": len(template.split())
            }
        # Unpaid and crawler share (whichever is filled)
        shared_template = filled_prompts.get("unpaid") or filled_prompts.get("crawler")
        if shared_template:
            for prompt_type in ["unpaid", "crawler"]:
                prompts_obj[prompt_type] = {
                    "template": shared_template,
                    "character_count": len(shared_template),
                    "word_count": len(shared_template.split())
                }
    elif variant_strategy == "unpaid_unique":
        # Unpaid is unique, paid/crawler share
        if "unpaid" in filled_prompts:
            template = filled_prompts["unpaid"]
            prompts_obj["unpaid"] = {
                "template": template,
                "character_count": len(template),
                "word_count": len(template.split())
            }
        # Paid and crawler share (whichever is filled)
        shared_template = filled_prompts.get("paid") or filled_prompts.get("crawler")
        if shared_template:
            for prompt_type in ["paid", "crawler"]:
                prompts_obj[prompt_type] = {
                    "template": shared_template,
                    "character_count": len(shared_template),
                    "word_count": len(shared_template.split())
                }
    elif variant_strategy == "crawler_unique":
        # Crawler is unique, paid/unpaid share
        if "crawler" in filled_prompts:
            template = filled_prompts["crawler"]
            prompts_obj["crawler"] = {
                "template": template,
                "character_count": len(template),
                "word_count": len(template.split())
            }
        # Paid and unpaid share (whichever is filled)
        shared_template = filled_prompts.get("paid") or filled_prompts.get("unpaid")
        if shared_template:
            for prompt_type in ["paid", "unpaid"]:
                prompts_obj[prompt_type] = {
                    "template": shared_template,
                    "character_count": len(shared_template),
                    "word_count": len(shared_template.split())
                }

    return prompts_obj


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

        # Extract prompts and variant_strategy from request
        prompts_input = prompts_data.get("prompts", {})
        variant_strategy = prompts_data.get("variant_strategy", "all_same")

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

        # First, collect all non-empty prompts
        filled_prompts = {}
        for prompt_type in valid_types:
            if prompt_type in prompts_input:
                template = prompts_input[prompt_type].get("template", "")
                if template.strip():
                    filled_prompts[prompt_type] = template

        if not filled_prompts:
            raise HTTPException(status_code=400, detail="No valid prompts provided")

        # Apply variant strategy mapping to determine which prompts to save
        prompts_obj = {}

        if variant_strategy == "all_same":
            # All types use the paid prompt - save all 3 with same content
            if "paid" in filled_prompts:
                template = filled_prompts["paid"]
                for prompt_type in valid_types:
                    prompts_obj[prompt_type] = {
                        "template": template,
                        "character_count": len(template),
                        "word_count": len(template.split())
                    }
        elif variant_strategy == "all_unique":
            # Each type uses its own prompt - save only what's filled
            for prompt_type in valid_types:
                if prompt_type in filled_prompts:
                    template = filled_prompts[prompt_type]
                    prompts_obj[prompt_type] = {
                        "template": template,
                        "character_count": len(template),
                        "word_count": len(template.split())
                    }
        elif variant_strategy == "paid_unique":
            # Paid is unique, unpaid/crawler share
            if "paid" in filled_prompts:
                template = filled_prompts["paid"]
                prompts_obj["paid"] = {
                    "template": template,
                    "character_count": len(template),
                    "word_count": len(template.split())
                }
            # Unpaid and crawler share (whichever is filled)
            shared_template = filled_prompts.get("unpaid") or filled_prompts.get("crawler")
            if shared_template:
                for prompt_type in ["unpaid", "crawler"]:
                    prompts_obj[prompt_type] = {
                        "template": shared_template,
                        "character_count": len(shared_template),
                        "word_count": len(shared_template.split())
                    }
        elif variant_strategy == "unpaid_unique":
            # Unpaid is unique, paid/crawler share
            if "unpaid" in filled_prompts:
                template = filled_prompts["unpaid"]
                prompts_obj["unpaid"] = {
                    "template": template,
                    "character_count": len(template),
                    "word_count": len(template.split())
                }
            # Paid and crawler share (whichever is filled)
            shared_template = filled_prompts.get("paid") or filled_prompts.get("crawler")
            if shared_template:
                for prompt_type in ["paid", "crawler"]:
                    prompts_obj[prompt_type] = {
                        "template": shared_template,
                        "character_count": len(shared_template),
                        "word_count": len(shared_template.split())
                    }
        elif variant_strategy == "crawler_unique":
            # Crawler is unique, paid/unpaid share
            if "crawler" in filled_prompts:
                template = filled_prompts["crawler"]
                prompts_obj["crawler"] = {
                    "template": template,
                    "character_count": len(template),
                    "word_count": len(template.split())
                }
            # Paid and unpaid share (whichever is filled)
            shared_template = filled_prompts.get("paid") or filled_prompts.get("unpaid")
            if shared_template:
                for prompt_type in ["paid", "unpaid"]:
                    prompts_obj[prompt_type] = {
                        "template": shared_template,
                        "character_count": len(shared_template),
                        "word_count": len(shared_template.split())
                    }

        if not prompts_obj:
            raise HTTPException(status_code=400, detail="No valid prompts after applying variant strategy")

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
            variant_strategy=variant_strategy,  # Include variant strategy
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
            - selected_models: Array of model IDs for testing (e.g., ["gpt-4o", "claude-sonnet-4-5"])
            - temperature: Generation temperature (0.0-1.0)
            - max_tokens: Maximum tokens to generate (50-4000)

    Example:
        ```json
        {
            "selected_models": ["gpt-4o", "claude-sonnet-4-5"],
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

        # Validation: At least one model is required for testing
        if not selected_models or not isinstance(selected_models, list) or len(selected_models) == 0:
            raise HTTPException(status_code=400, detail="At least one model must be selected")

        # Validation: Temperature range (0.0 - 1.0)
        if not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 1.0:
            raise HTTPException(status_code=400, detail="Temperature must be between 0.0 and 1.0")

        # Validation: Max tokens range (50 - 4000)
        if not isinstance(max_tokens, int) or max_tokens < 50 or max_tokens > 4000:
            raise HTTPException(status_code=400, detail="Max tokens must be between 50 and 4000")

        # Validate all model IDs against available models
        from ..llm_providers import ProviderRegistry
        available_models = ProviderRegistry.list_available_models()
        available_model_ids = {model["model_id"] for model in available_models}

        for model_id in selected_models:
            if model_id not in available_model_ids:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model ID: {model_id}. Use /api/news/models to see available models."
                )

        # Build model_config object (array format for testing multiple models)
        model_config_data = {
            "selected_models": selected_models,  # Array of model IDs for testing
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
                        "llm_config": model_config_data,  # Use llm_config (renamed to avoid Pydantic conflict)
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
                "llm_config": model_config_data,  # Use llm_config (renamed to avoid Pydantic conflict)
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
            f"models={selected_models}, temp={temperature}, max_tokens={max_tokens}"
        )

        return {
            "success": True,
            "message": f"Model configuration saved to draft for '{trigger_name}'",
            "llm_config": model_config_data,
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

        if draft_doc:
            # Check for llm_config (new) and old field names (model_config, model_config_data) for backward compatibility
            model_config_data = draft_doc.get("llm_config") or draft_doc.get("model_config") or draft_doc.get("model_config_data")
            if model_config_data:
                is_draft = True

        if not model_config_data:
            # Fall back to published configuration
            trigger_doc = await db.trigger_prompts.find_one({"trigger_name": trigger_name})
            if trigger_doc:
                # Check for llm_config (new) and old field names (model_config, model_config_data) for backward compatibility
                model_config_data = trigger_doc.get("llm_config") or trigger_doc.get("model_config") or trigger_doc.get("model_config_data")
                is_draft = False

        # Return defaults if no configuration found
        if not model_config_data:
            return {
                "trigger_name": trigger_name,
                "llm_config": {
                    "selected_models": [],  # Empty array for testing
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "updated_at": None
                },
                "is_configured": False,
                "is_draft": False,
                "message": "No model configuration set. Use POST to configure models."
            }

        # Handle both formats: selected_models array (testing) or model string (legacy)
        selected_models = model_config_data.get("selected_models")
        if selected_models and isinstance(selected_models, list):
            # Current format: array for testing
            pass
        elif model_config_data.get("model"):
            # Legacy format: single model string - convert to array
            selected_models = [model_config_data.get("model")]
        else:
            selected_models = []

        return {
            "trigger_name": trigger_name,
            "llm_config": {
                "selected_models": selected_models,  # Array for testing multiple models
                "temperature": model_config_data.get("temperature", 0.7),
                "max_tokens": model_config_data.get("max_tokens", 500),
                "updated_at": model_config_data.get("updated_at").isoformat() if model_config_data.get("updated_at") else None
            },
            "is_configured": len(selected_models) > 0,
            "is_draft": is_draft
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
        # Get database connection
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

        # Extract components from payload
        prompts_data = draft_data.get("prompts", {})
        model_config = draft_data.get("llm_config", {})
        data_config = draft_data.get("data_config", {})
        variant_strategy = draft_data.get("variant_strategy", "all_same")
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

        # Apply variant strategy mapping to prompts
        processed_prompts = apply_variant_strategy_mapping(prompts_data, variant_strategy)

        if not processed_prompts:
            raise HTTPException(
                status_code=400,
                detail="No valid prompts after applying variant strategy. Please fill at least one prompt."
            )

        # Prepare complete draft document
        draft_document = {
            "trigger_name": trigger_name,
            "prompts": processed_prompts,  # Use processed prompts with strategy applied
            "llm_config": model_config if model_config else None,
            "data_config": data_config if data_config else None,
            "variant_strategy": variant_strategy,  # Save variant strategy with draft
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
                "llm_config": bool(model_config),
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
        "published_by": "user123",  // optional, who published
        "notes": "Publishing notes",  // optional publishing notes
        "model_settings": {  // optional, override model selection
            "selected_models": ["gpt-4o"],  // MUST contain exactly 1 model
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }

    If model_settings is provided, it will be used instead of the draft's model_config_data.
    This allows selecting a single production model at publish time.

    After publishing, the draft remains in trigger_prompt_drafts for history tracking.
    """
    try:
        # Get database connection
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")

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

        # Extract payload parameters
        published_by = "system"
        publishing_notes = ""

        # Build model_config for production (provider + model + temperature)
        llm_config_draft = latest_draft.get("llm_config", {})

        # Helper function to determine provider from model name
        def get_provider_from_model(model_name):
            model_lower = model_name.lower()
            if "gpt" in model_lower:
                return "openai"
            elif "claude" in model_lower:
                return "anthropic"
            elif "gemini" in model_lower:
                return "google"
            return "openai"  # default

        if publish_data and isinstance(publish_data, dict):
            published_by = publish_data.get("published_by", "system")
            publishing_notes = publish_data.get("notes", "")

            # Check if user provided model at publish time
            if "model_settings" in publish_data:
                user_model_settings = publish_data["model_settings"]
                user_models = user_model_settings.get("selected_models", [])

                if len(user_models) != 1:
                    raise HTTPException(
                        status_code=400,
                        detail="Exactly one model must be selected for production. "
                               f"Received {len(user_models)} models."
                    )

                selected_model = user_models[0]
                temperature = user_model_settings.get("temperature", 0.7)
                logger.info(f"Using user-selected model for production: {selected_model}")
            else:
                # Use from draft
                draft_models = llm_config_draft.get("selected_models", [])
                selected_model = draft_models[0] if draft_models else "gpt-4o-mini"
                temperature = llm_config_draft.get("temperature", 0.7)
        else:
            # No publish_data provided, use from draft
            draft_models = llm_config_draft.get("selected_models", [])
            selected_model = draft_models[0] if draft_models else "gpt-4o-mini"
            temperature = llm_config_draft.get("temperature", 0.7)

        # Build production model_config structure (provider, model, temperature)
        model_config_to_use = {
            "provider": get_provider_from_model(selected_model),
            "model": selected_model,
            "temperature": temperature
        }

        # Check if trigger exists in production
        existing_trigger = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

        if not existing_trigger:
            raise HTTPException(
                status_code=404,
                detail=f"Trigger '{trigger_name}' not found in trigger_prompts collection"
            )

        # Transform data_config to production format (handle field name differences)
        draft_data_config = latest_draft.get("data_config", {})
        production_data_config = {
            "sections": draft_data_config.get("sections", draft_data_config.get("selected_sections", [])),
            "section_order": draft_data_config.get("section_order", []),
            "data_mode": draft_data_config.get("data_mode", "new")
        }

        # Transform prompts: extract template strings from draft objects for production
        published_prompts = {}
        for prompt_type, prompt_data in latest_draft.get("prompts", {}).items():
            if isinstance(prompt_data, dict) and "template" in prompt_data:
                # Extract template string from draft object
                published_prompts[prompt_type] = prompt_data["template"]
            elif isinstance(prompt_data, str):
                # Already a string (backward compatibility)
                published_prompts[prompt_type] = prompt_data

        # Get current version and increment for new publication
        current_version = existing_trigger.get("version", 0)
        new_version = current_version + 1

        # Prepare update fields (only update CMS-managed configuration, preserve other fields)
        update_fields = {
            "prompts": published_prompts,  # {paid, unpaid, crawler} as plain strings
            "model_config": model_config_to_use,  # {provider, model, temperature}
            "data_config": production_data_config,  # {sections, section_order, data_mode}
            "variant_strategy": latest_draft.get("variant_strategy", "all_same"),
            "system_prompt": latest_draft.get("system_prompt", ""),  # System prompt if exists
            "version": new_version,  # Incremented version number
            "updated_at": datetime.utcnow(),  # Timestamp of update
            "published_at": datetime.utcnow(),  # Timestamp of publication
            "published_by": published_by  # User who published
        }

        # Update the trigger_prompts collection (only update specified fields)
        update_result = await db.trigger_prompts.update_one(
            {"trigger_name": trigger_name},
            {"$set": update_fields}
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
            "version": new_version,
            "published_at": update_fields["published_at"].isoformat(),
            "updated_at": update_fields["updated_at"].isoformat(),
            "published_by": published_by,
            "components_published": {
                "prompts": len(published_prompts),
                "model_config": bool(model_config_to_use),
                "data_config": bool(production_data_config),
                "variant_strategy": update_fields["variant_strategy"]
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
        db = get_database()

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


@router.post("/{trigger_name}/validate")
async def validate_configuration(trigger_name: str, validation_data: dict):
    """
    Validate trigger configuration before publishing (Story 5.1)

    Validates:
    - Prompt templates not empty for enabled types
    - At least one API configured
    - Section order defined
    - Model selected
    - Successful test generation exists for each prompt type
    - Generation results are acceptable (not empty, reasonable cost)

    Request body:
    {
        "apis": ["earnings_api", "price_data_api"],
        "section_order": ["company_overview", "financial_data"],
        "prompts": {
            "paid": "Generate article...",
            "unpaid": "Generate article...",
            "crawler": "Generate article..."
        },
        "model_settings": {
            "selected_models": ["gpt-4o", "claude-3.5-sonnet"],
            "temperature": 0.7,
            "max_tokens": 500
        },
        "enabled_prompt_types": ["paid", "unpaid", "crawler"],
        "session_id": "test-1234567890"  # Optional
    }

    Returns validation result with issues grouped by prompt type
    """
    try:
        from ..services.validation_service import get_validation_service

        # Extract validation data
        apis = validation_data.get("apis", [])
        section_order = validation_data.get("section_order", [])
        prompts = validation_data.get("prompts", {})
        model_settings = validation_data.get("model_settings", {})
        enabled_prompt_types = validation_data.get("enabled_prompt_types", ["paid", "unpaid", "crawler"])
        session_id = validation_data.get("session_id")

        # Get validation service
        validation_service = get_validation_service(db)

        # Run validation
        validation_result = await validation_service.validate_configuration(
            trigger_id=trigger_name,
            apis=apis,
            section_order=section_order,
            prompts=prompts,
            model_settings=model_settings,
            enabled_prompt_types=enabled_prompt_types,
            session_id=session_id
        )

        # Convert to dict for response
        return {
            "success": True,
            "is_valid": validation_result.is_valid,
            "prompt_types": {
                pt: {
                    "prompt_type": result.prompt_type,
                    "is_valid": result.is_valid,
                    "issues": [issue.dict() for issue in result.issues],
                    "test_metadata": result.test_metadata
                }
                for pt, result in validation_result.prompt_types.items()
            },
            "shared_config_issues": [issue.dict() for issue in validation_result.shared_config_issues],
            "summary": validation_result.summary
        }

    except Exception as e:
        logger.error(f"Validation failed for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/{trigger_name}/publish-new")
async def publish_configuration(trigger_name: str, publish_data: dict):
    """
    Publish trigger configuration to production (Story 5.2 - New workflow)

    Request body:
    {
        "apis": ["earnings_api", "price_data_api"],
        "section_order": ["company_overview", "financial_data"],
        "prompts": {
            "paid": "Generate article...",
            "unpaid": "Generate article...",
            "crawler": "Generate article..."
        },
        "model_settings": {
            "selected_models": ["gpt-4o", "claude-3.5-sonnet"],
            "temperature": 0.7,
            "max_tokens": 500
        },
        "test_results_summary": {
            "paid": {
                "models_tested": ["gpt-4o", "claude-3.5-sonnet"],
                "avg_cost": 0.42,
                "avg_latency": 8.5,
                "total_tests": 2,
                "sample_output_preview": "Apple Inc. reported..."
            }
        },
        "published_by": "user123",
        "notes": "Optional publishing notes"
    }

    Returns:
    {
        "success": true,
        "message": "Configuration published successfully as version 5",
        "trigger_id": "earnings",
        "version": 5,
        "published_at": "2025-11-06T14:30:00Z",
        "is_active": true
    }
    """
    try:
        from ..services.publishing_service import get_publishing_service
        from ..models.published_config import PublishRequest, TestResultsSummary

        # Parse test_results_summary
        test_results_summary = {}
        raw_test_results = publish_data.get("test_results_summary", {})
        for prompt_type, summary_data in raw_test_results.items():
            test_results_summary[prompt_type] = TestResultsSummary(**summary_data)

        # Create publish request
        publish_request = PublishRequest(
            apis=publish_data.get("apis", []),
            section_order=publish_data.get("section_order", []),
            prompts=publish_data.get("prompts", {}),
            model_settings=publish_data.get("model_settings", {}),
            test_results_summary=test_results_summary,
            published_by=publish_data.get("published_by", "unknown"),
            notes=publish_data.get("notes")
        )

        # Get publishing service
        publishing_service = get_publishing_service(db)

        # Publish configuration
        response = await publishing_service.publish_configuration(
            trigger_id=trigger_name,
            publish_request=publish_request
        )

        return response.model_dump()

    except Exception as e:
        logger.error(f"Publishing failed for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")


@router.get("/{trigger_name}/published")
async def get_active_published_config(trigger_name: str):
    """
    Get the active published configuration for a trigger (Story 5.2)

    Returns the currently active published configuration with version info
    """
    try:
        from ..services.publishing_service import get_publishing_service

        publishing_service = get_publishing_service(db)
        config = await publishing_service.get_active_configuration(trigger_name)

        if not config:
            raise HTTPException(status_code=404, detail="No published configuration found")

        return config.model_dump()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get published config for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve published config: {str(e)}")


@router.get("/{trigger_name}/audit-logs")
async def get_audit_logs(
    trigger_name: str,
    action: Optional[str] = None,
    performed_by: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """
    Get audit logs for a trigger (Story 5.3)

    Query parameters:
    - action: Filter by action type (publish, rollback, etc.)
    - performed_by: Filter by user ID
    - limit: Maximum number of results (default 50, max 500)
    - skip: Number of results to skip for pagination
    """
    try:
        from ..services.audit_service import get_audit_service
        from ..models.audit_log import AuditLogFilter

        # Create filter
        filter_params = AuditLogFilter(
            trigger_id=trigger_name,
            action=action,
            performed_by=performed_by,
            limit=min(limit, 500),
            skip=skip
        )

        # Get audit service and query logs
        audit_service = get_audit_service(db)
        logs = await audit_service.get_audit_logs(filter_params)

        return {
            "success": True,
            "logs": [log.model_dump() for log in logs],
            "count": len(logs),
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Failed to get audit logs for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit logs: {str(e)}")


@router.get("/{trigger_name}/audit-stats")
async def get_audit_stats(trigger_name: str):
    """
    Get audit statistics for a trigger (Story 5.3)

    Returns statistics like total publishes, rollbacks, success rate, etc.
    """
    try:
        from ..services.audit_service import get_audit_service

        audit_service = get_audit_service(db)
        stats = await audit_service.get_stats(trigger_name)

        return {
            "success": True,
            "stats": stats.model_dump()
        }

    except Exception as e:
        logger.error(f"Failed to get audit stats for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit stats: {str(e)}")


@router.get("/{trigger_name}/versions")
async def get_all_versions(trigger_name: str, limit: int = 50):
    """
    Get all published versions for a trigger (Story 5.4)

    Query parameters:
    - limit: Maximum number of versions to return (default 50)

    Returns list of all published configurations, newest first
    """
    try:
        from ..services.publishing_service import get_publishing_service

        publishing_service = get_publishing_service(db)
        versions = await publishing_service.get_all_versions(trigger_name, limit=limit)

        return {
            "success": True,
            "versions": [version.model_dump() for version in versions],
            "count": len(versions)
        }

    except Exception as e:
        logger.error(f"Failed to get versions for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve versions: {str(e)}")


@router.get("/{trigger_name}/versions/{version}")
async def get_version_by_number(trigger_name: str, version: int):
    """
    Get a specific version of published configuration (Story 5.4)

    Returns the complete configuration snapshot for the specified version
    """
    try:
        from ..services.publishing_service import get_publishing_service

        publishing_service = get_publishing_service(db)
        config = await publishing_service.get_configuration_by_version(trigger_name, version)

        if not config:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")

        return {
            "success": True,
            "version": config.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get version {version} for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve version: {str(e)}")


@router.post("/{trigger_name}/versions/{version}/compare")
async def compare_versions(trigger_name: str, version: int, compare_data: dict):
    """
    Compare two versions of configuration (Story 5.4)

    Request body:
    {
        "compare_with_version": 4
    }

    Returns a detailed diff between the two versions
    """
    try:
        from ..services.publishing_service import get_publishing_service

        compare_with_version = compare_data.get("compare_with_version")
        if not compare_with_version:
            raise HTTPException(status_code=400, detail="compare_with_version is required")

        publishing_service = get_publishing_service(db)

        # Get both versions
        version_a = await publishing_service.get_configuration_by_version(trigger_name, version)
        version_b = await publishing_service.get_configuration_by_version(trigger_name, compare_with_version)

        if not version_a:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")
        if not version_b:
            raise HTTPException(status_code=404, detail=f"Version {compare_with_version} not found")

        # Compare configurations
        diff = {
            "version_a": version,
            "version_b": compare_with_version,
            "differences": {}
        }

        # Compare APIs
        if set(version_a.apis) != set(version_b.apis):
            diff["differences"]["apis"] = {
                "version_a": version_a.apis,
                "version_b": version_b.apis,
                "added": list(set(version_b.apis) - set(version_a.apis)),
                "removed": list(set(version_a.apis) - set(version_b.apis))
            }

        # Compare section order
        if version_a.section_order != version_b.section_order:
            diff["differences"]["section_order"] = {
                "version_a": version_a.section_order,
                "version_b": version_b.section_order
            }

        # Compare prompts
        prompt_diffs = {}
        all_prompt_types = set(version_a.prompts.keys()) | set(version_b.prompts.keys())
        for prompt_type in all_prompt_types:
            prompt_a = version_a.prompts.get(prompt_type, "")
            prompt_b = version_b.prompts.get(prompt_type, "")
            if prompt_a != prompt_b:
                prompt_diffs[prompt_type] = {
                    "version_a": prompt_a,
                    "version_b": prompt_b,
                    "changed": prompt_a != prompt_b
                }
        if prompt_diffs:
            diff["differences"]["prompts"] = prompt_diffs

        # Compare model settings
        if version_a.model_settings != version_b.model_settings:
            diff["differences"]["model_settings"] = {
                "version_a": version_a.model_settings,
                "version_b": version_b.model_settings
            }

        # Compare test results summary
        if version_a.test_results_summary != version_b.test_results_summary:
            diff["differences"]["test_results_summary"] = {
                "version_a": {k: v.model_dump() for k, v in version_a.test_results_summary.items()},
                "version_b": {k: v.model_dump() for k, v in version_b.test_results_summary.items()}
            }

        return {
            "success": True,
            "diff": diff,
            "has_differences": len(diff["differences"]) > 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compare versions for trigger '{trigger_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare versions: {str(e)}")


@router.post("/{trigger_name}/versions/{version}/rollback")
async def rollback_to_version(trigger_name: str, version: int, rollback_data: dict):
    """
    Rollback to a previous version (Story 5.4)

    Request body:
    {
        "performed_by": "user123"
    }

    Creates a new version that's a copy of the target version
    """
    try:
        from ..services.publishing_service import get_publishing_service

        performed_by = rollback_data.get("performed_by", "unknown")

        publishing_service = get_publishing_service(db)
        response = await publishing_service.rollback_to_version(
            trigger_id=trigger_name,
            target_version=version,
            published_by=performed_by
        )

        return response.model_dump()

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to rollback trigger '{trigger_name}' to version {version}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rollback: {str(e)}")
