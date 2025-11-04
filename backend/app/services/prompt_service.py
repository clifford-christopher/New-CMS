"""
Prompt resolution service.
Implements logic to check CMS-managed prompts first, then fall back to legacy prompts.
"""
from typing import Optional, Union
from ..database import get_database
from ..models import TriggerPrompt, Configuration
import logging

logger = logging.getLogger(__name__)


async def get_active_prompt(trigger_key: str) -> Optional[Union[Configuration, TriggerPrompt]]:
    """
    Retrieve the active prompt configuration for a given trigger.

    Priority:
    1. Check configurations collection for CMS-managed version (is_active=True)
    2. Fall back to trigger_prompts collection for legacy version

    Args:
        trigger_key: Unique trigger identifier (e.g., "52_week_high_summary")

    Returns:
        Configuration object (CMS-managed) or TriggerPrompt object (legacy), or None if not found
    """
    db = get_database()

    # 1. Check for CMS-managed configuration (highest priority)
    cms_prompt_data = await db.configurations.find_one({
        "trigger_key": trigger_key,
        "is_active": True
    })

    if cms_prompt_data:
        logger.info(f"Using CMS-managed prompt for trigger: {trigger_key}")
        return Configuration(**cms_prompt_data)

    # 2. Fall back to legacy trigger_prompts
    legacy_prompt_data = await db.trigger_prompts.find_one({
        "trigger_key": trigger_key
    })

    if legacy_prompt_data:
        logger.info(f"Using legacy prompt for trigger: {trigger_key}")
        # Convert ObjectId and datetime to strings for Pydantic validation
        legacy_prompt_data["_id"] = str(legacy_prompt_data["_id"])
        if "metadata" in legacy_prompt_data:
            for date_field in ["created_at", "updated_at", "extraction_date"]:
                if date_field in legacy_prompt_data["metadata"]:
                    legacy_prompt_data["metadata"][date_field] = str(legacy_prompt_data["metadata"][date_field])
        if "special_handling" in legacy_prompt_data and legacy_prompt_data["special_handling"].get("irb_stock_id"):
            legacy_prompt_data["special_handling"]["irb_stock_id"] = str(legacy_prompt_data["special_handling"]["irb_stock_id"])
        return TriggerPrompt(**legacy_prompt_data)

    # 3. Not found in either collection
    logger.warning(f"No prompt found for trigger: {trigger_key}")
    return None


async def get_all_prompts():
    """
    Retrieve all prompts, prioritizing CMS-managed versions.

    Returns:
        List of prompt configurations (CMS-managed and legacy)
    """
    db = get_database()

    # Get all CMS-managed prompts
    cms_prompts = []
    async for doc in db.configurations.find({"is_active": True}):
        cms_prompts.append(Configuration(**doc))

    cms_trigger_keys = {p.trigger_key for p in cms_prompts}

    # Get legacy prompts that don't have CMS versions
    legacy_prompts = []
    async for doc in db.trigger_prompts.find({}):
        if doc["trigger_key"] not in cms_trigger_keys:
            # Convert ObjectId and datetime to strings for Pydantic validation
            doc["_id"] = str(doc["_id"])
            if "metadata" in doc:
                for date_field in ["created_at", "updated_at", "extraction_date"]:
                    if date_field in doc["metadata"]:
                        doc["metadata"][date_field] = str(doc["metadata"][date_field])
            if "special_handling" in doc and doc["special_handling"].get("irb_stock_id"):
                doc["special_handling"]["irb_stock_id"] = str(doc["special_handling"]["irb_stock_id"])
            legacy_prompts.append(TriggerPrompt(**doc))

    return cms_prompts + legacy_prompts
