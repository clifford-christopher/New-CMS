"""
Unit tests for prompt resolution logic
"""
import pytest
from app.services.prompt_service import get_active_prompt, get_all_prompts
from app.database import connect_to_mongo, close_mongo_connection
from app.models import Configuration, TriggerPrompt


@pytest.mark.asyncio
async def test_get_active_prompt_legacy():
    """Test get_active_prompt returns legacy prompt when no CMS version exists"""
    await connect_to_mongo()

    # Use a trigger_key that we know exists in trigger_prompts
    prompt = await get_active_prompt("52_week_high_summary")

    assert prompt is not None
    # Should be TriggerPrompt since no CMS version exists
    assert isinstance(prompt, TriggerPrompt)
    assert prompt.trigger_key == "52_week_high_summary"

    await close_mongo_connection()


@pytest.mark.asyncio
async def test_get_active_prompt_not_found():
    """Test get_active_prompt returns None for non-existent trigger"""
    await connect_to_mongo()

    prompt = await get_active_prompt("nonexistent_trigger_key_12345")
    assert prompt is None

    await close_mongo_connection()


@pytest.mark.asyncio
async def test_get_all_prompts_returns_list():
    """Test get_all_prompts returns list of prompts"""
    await connect_to_mongo()

    prompts = await get_all_prompts()

    assert isinstance(prompts, list)
    assert len(prompts) > 0  # Should have at least 54 legacy prompts

    # All should be either Configuration or TriggerPrompt
    for prompt in prompts:
        assert isinstance(prompt, (Configuration, TriggerPrompt))

    await close_mongo_connection()


@pytest.mark.asyncio
async def test_get_all_prompts_no_duplicates():
    """Test get_all_prompts doesn't return duplicates"""
    await connect_to_mongo()

    prompts = await get_all_prompts()

    trigger_keys = [p.trigger_key for p in prompts]
    # Check no duplicates
    assert len(trigger_keys) == len(set(trigger_keys))

    await close_mongo_connection()


@pytest.mark.asyncio
async def test_prompt_has_required_fields():
    """Test returned prompt has required fields"""
    await connect_to_mongo()

    prompt = await get_active_prompt("52_week_high_summary")

    if prompt:
        assert hasattr(prompt, "trigger_key")
        assert hasattr(prompt, "prompts")
        assert isinstance(prompt.prompts, dict)
        # Should have paid, unpaid, crawler variants
        assert "paid" in prompt.prompts or hasattr(prompt.prompts.get("paid"), "article")

    await close_mongo_connection()
