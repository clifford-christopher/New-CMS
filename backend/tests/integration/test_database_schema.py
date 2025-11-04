"""
Integration tests for News CMS Workflow database schema.
Tests end-to-end workflow with MongoDB collections.
"""
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from app.models.trigger_prompt_config import (
    TriggerPromptConfig,
    DataConfig,
    LLMConfig,
    PromptTemplates,
    DataMode,
    LLMProvider
)
from app.models.generation_history import GenerationHistory
from app.models.prompt_version import PromptVersion


@pytest.fixture
async def mongodb_client():
    """Create test MongoDB client."""
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["mmfrontend_test"]

    # Clean up test collections before tests
    await db.trigger_prompts.delete_many({})
    await db.generation_history.delete_many({})
    await db.prompt_versions.delete_many({})

    yield db

    # Clean up after tests
    await db.trigger_prompts.delete_many({})
    await db.generation_history.delete_many({})
    await db.prompt_versions.delete_many({})
    client.close()


class TestTriggerPromptConfigIntegration:
    """Integration tests for trigger_prompts collection."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_config(self, mongodb_client):
        """Test creating and retrieving TriggerPromptConfig."""
        config = TriggerPromptConfig(
            trigger_name="earnings_result_test",
            isActive=True,
            llm_config=LLMConfig(
                provider=LLMProvider.CLAUDE,
                model="claude-sonnet-4-5-20250929",
                temperature=0.7,
                max_tokens=20000
            ),
            data_config=DataConfig(
                data_mode=DataMode.NEW,
                sections=[1, 2, 3, 5, 7],
                section_order=[1, 2, 3, 5, 7]
            ),
            prompts=PromptTemplates(
                paid="Generate article for {trigger_name}...",
                unpaid="Generate summary for {trigger_name}..."
            )
        )

        # Insert into MongoDB
        result = await mongodb_client.trigger_prompts.insert_one(
            config.model_dump(by_alias=True)
        )
        assert result.inserted_id is not None

        # Retrieve from MongoDB
        doc = await mongodb_client.trigger_prompts.find_one(
            {"trigger_name": "earnings_result_test"}
        )
        assert doc is not None

        # Reconstruct model
        retrieved = TriggerPromptConfig(**doc)
        assert retrieved.trigger_name == "earnings_result_test"
        assert retrieved.isActive is True
        assert retrieved.llm_config.provider == LLMProvider.CLAUDE
        assert retrieved.data_config.data_mode == DataMode.NEW
        assert retrieved.prompts.paid == "Generate article for {trigger_name}..."

    @pytest.mark.asyncio
    async def test_unique_trigger_name_constraint(self, mongodb_client):
        """Test trigger_name uniqueness is enforced."""
        # Create unique index
        await mongodb_client.trigger_prompts.create_index(
            "trigger_name",
            unique=True
        )

        config1 = TriggerPromptConfig(trigger_name="test_unique")
        await mongodb_client.trigger_prompts.insert_one(
            config1.model_dump(by_alias=True)
        )

        # Attempt duplicate insert
        config2 = TriggerPromptConfig(trigger_name="test_unique")
        with pytest.raises(Exception):  # MongoDB duplicate key error
            await mongodb_client.trigger_prompts.insert_one(
                config2.model_dump(by_alias=True)
            )

    @pytest.mark.asyncio
    async def test_update_config_increments_version(self, mongodb_client):
        """Test updating config increments version."""
        config = TriggerPromptConfig(
            trigger_name="test_versioning",
            version=1
        )
        await mongodb_client.trigger_prompts.insert_one(
            config.model_dump(by_alias=True)
        )

        # Update and increment version
        await mongodb_client.trigger_prompts.update_one(
            {"trigger_name": "test_versioning"},
            {
                "$set": {"updated_at": datetime.now(datetime.UTC)},
                "$inc": {"version": 1}
            }
        )

        # Verify version incremented
        doc = await mongodb_client.trigger_prompts.find_one(
            {"trigger_name": "test_versioning"}
        )
        assert doc["version"] == 2

    @pytest.mark.asyncio
    async def test_backward_compatibility_with_legacy_docs(self, mongodb_client):
        """Test backward compatibility with legacy documents."""
        # Insert legacy document (no new fields)
        legacy_doc = {
            "trigger_name": "legacy_trigger"
        }
        await mongodb_client.trigger_prompts.insert_one(legacy_doc)

        # Retrieve and reconstruct with Pydantic
        doc = await mongodb_client.trigger_prompts.find_one(
            {"trigger_name": "legacy_trigger"}
        )
        config = TriggerPromptConfig(**doc)

        # Should use default values
        assert config.isActive is False
        assert config.llm_config is None
        assert config.data_config is None
        assert config.prompts is None


class TestGenerationHistoryIntegration:
    """Integration tests for generation_history collection."""

    @pytest.mark.asyncio
    async def test_track_successful_generation(self, mongodb_client):
        """Test tracking successful news generation."""
        history = GenerationHistory(
            trigger_name="earnings_result",
            stockid=12345,
            prompt_type="paid",
            data_mode="new",
            model="claude-sonnet-4-5-20250929",
            input_data={"section_1": {"revenue": 123.4}},
            prompt_used="Generate article...",
            generated_html="<article>Content</article>",
            extracted_title="Apple Earnings",
            extracted_summary="Apple reported...",
            extracted_article="<p>Full article...</p>",
            method="new",
            tokens_used=15000,
            cost=0.45,
            generation_time=3.5,
            status="success"
        )

        # Insert into MongoDB
        result = await mongodb_client.generation_history.insert_one(
            history.model_dump(by_alias=True)
        )
        assert result.inserted_id is not None

        # Query by trigger + stockid
        doc = await mongodb_client.generation_history.find_one({
            "trigger_name": "earnings_result",
            "stockid": 12345
        })
        assert doc is not None
        assert doc["status"] == "success"
        assert doc["cost"] == 0.45

    @pytest.mark.asyncio
    async def test_track_failed_generation(self, mongodb_client):
        """Test tracking failed news generation."""
        history = GenerationHistory(
            trigger_name="earnings_result",
            stockid=67890,
            prompt_type="paid",
            data_mode="new",
            model="gpt-4o",
            input_data={},
            prompt_used="Generate article...",
            generated_html="",
            extracted_title="",
            extracted_summary="",
            extracted_article="",
            method="new",
            tokens_used=0,
            cost=0.0,
            generation_time=0.5,
            status="failed",
            error_message="LLM API timeout after 30 seconds"
        )

        result = await mongodb_client.generation_history.insert_one(
            history.model_dump(by_alias=True)
        )
        assert result.inserted_id is not None

        # Query failed generations
        failed_count = await mongodb_client.generation_history.count_documents({
            "status": "failed"
        })
        assert failed_count == 1

    @pytest.mark.asyncio
    async def test_analytics_query_by_trigger(self, mongodb_client):
        """Test analytics query - total cost per trigger."""
        # Insert multiple generations
        for i in range(3):
            history = GenerationHistory(
                trigger_name="earnings_result",
                stockid=i,
                prompt_type="paid",
                data_mode="new",
                model="claude-sonnet-4-5-20250929",
                input_data={},
                prompt_used="test",
                generated_html="<html></html>",
                extracted_title="Title",
                extracted_summary="Summary",
                extracted_article="Article",
                method="new",
                tokens_used=10000,
                cost=0.30,
                generation_time=2.0,
                status="success"
            )
            await mongodb_client.generation_history.insert_one(
                history.model_dump(by_alias=True)
            )

        # Aggregate total cost
        pipeline = [
            {"$match": {"trigger_name": "earnings_result"}},
            {"$group": {
                "_id": "$trigger_name",
                "total_cost": {"$sum": "$cost"},
                "avg_tokens": {"$avg": "$tokens_used"},
                "generation_count": {"$sum": 1}
            }}
        ]
        result = await mongodb_client.generation_history.aggregate(pipeline).to_list(None)

        assert len(result) == 1
        assert result[0]["total_cost"] == 0.90  # 3 * 0.30
        assert result[0]["avg_tokens"] == 10000
        assert result[0]["generation_count"] == 3

    @pytest.mark.asyncio
    async def test_compound_index_performance(self, mongodb_client):
        """Test compound index on trigger_name + stockid + timestamp."""
        # Create compound index
        await mongodb_client.generation_history.create_index([
            ("trigger_name", 1),
            ("stockid", 1),
            ("timestamp", -1)
        ])

        # Insert test data
        for stockid in [100, 200, 300]:
            history = GenerationHistory(
                trigger_name="test_trigger",
                stockid=stockid,
                prompt_type="paid",
                data_mode="new",
                model="test",
                input_data={},
                prompt_used="test",
                generated_html="<html></html>",
                extracted_title="Title",
                extracted_summary="Summary",
                extracted_article="Article",
                method="new",
                tokens_used=100,
                cost=0.01,
                generation_time=1.0,
                status="success"
            )
            await mongodb_client.generation_history.insert_one(
                history.model_dump(by_alias=True)
            )

        # Query using compound index
        cursor = mongodb_client.generation_history.find({
            "trigger_name": "test_trigger",
            "stockid": 200
        }).sort("timestamp", -1)

        results = await cursor.to_list(None)
        assert len(results) == 1
        assert results[0]["stockid"] == 200


class TestPromptVersionIntegration:
    """Integration tests for prompt_versions collection."""

    @pytest.mark.asyncio
    async def test_create_version_on_publish(self, mongodb_client):
        """Test creating version snapshot on publish."""
        version = PromptVersion(
            trigger_name="earnings_result",
            version=1,
            llm_config={
                "provider": "claude",
                "model": "claude-sonnet-4-5-20250929"
            },
            data_config={
                "data_mode": "new",
                "sections": [1, 2, 3]
            },
            prompts={
                "paid": "Generate article..."
            },
            published_by="admin@example.com",
            test_generation_count=10,
            avg_cost_per_generation=0.35
        )

        result = await mongodb_client.prompt_versions.insert_one(
            version.model_dump(by_alias=True)
        )
        assert result.inserted_id is not None

    @pytest.mark.asyncio
    async def test_rollback_to_previous_version(self, mongodb_client):
        """Test rollback workflow."""
        # Create version 1 (working)
        v1 = PromptVersion(
            trigger_name="test_rollback",
            version=1,
            llm_config={"temperature": 0.7},
            data_config={},
            prompts={"paid": "Working prompt"},
            published_by="user1@example.com"
        )
        await mongodb_client.prompt_versions.insert_one(
            v1.model_dump(by_alias=True)
        )

        # Create version 2 (broken)
        v2 = PromptVersion(
            trigger_name="test_rollback",
            version=2,
            llm_config={"temperature": 1.5},  # Invalid
            data_config={},
            prompts={"paid": "Broken prompt"},
            published_by="user2@example.com"
        )
        await mongodb_client.prompt_versions.insert_one(
            v2.model_dump(by_alias=True)
        )

        # Rollback: Retrieve version 1
        v1_doc = await mongodb_client.prompt_versions.find_one({
            "trigger_name": "test_rollback",
            "version": 1
        })
        assert v1_doc is not None
        rollback_config = PromptVersion(**v1_doc)
        assert rollback_config.prompts["paid"] == "Working prompt"

        # Apply rollback to trigger_prompts
        await mongodb_client.trigger_prompts.update_one(
            {"trigger_name": "test_rollback"},
            {
                "$set": {
                    "llm_config": rollback_config.llm_config,
                    "prompts": rollback_config.prompts
                }
            },
            upsert=True
        )

        # Verify rollback applied
        current = await mongodb_client.trigger_prompts.find_one({
            "trigger_name": "test_rollback"
        })
        assert current["prompts"]["paid"] == "Working prompt"

    @pytest.mark.asyncio
    async def test_version_history_query(self, mongodb_client):
        """Test querying version history."""
        # Create 3 versions
        for v in range(1, 4):
            version = PromptVersion(
                trigger_name="test_history",
                version=v,
                llm_config={},
                data_config={},
                prompts={"paid": f"Version {v} prompt"},
                published_by=f"user{v}@example.com"
            )
            await mongodb_client.prompt_versions.insert_one(
                version.model_dump(by_alias=True)
            )

        # Query all versions for trigger (descending order)
        cursor = mongodb_client.prompt_versions.find({
            "trigger_name": "test_history"
        }).sort("version", -1)

        versions = await cursor.to_list(None)
        assert len(versions) == 3
        assert versions[0]["version"] == 3
        assert versions[1]["version"] == 2
        assert versions[2]["version"] == 1


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    @pytest.mark.asyncio
    async def test_complete_workflow_new_method(self, mongodb_client):
        """Test complete workflow: configure -> publish -> generate -> track."""
        # Step 1: Create configuration (isActive=false initially)
        config = TriggerPromptConfig(
            trigger_name="e2e_test",
            isActive=False,
            llm_config=LLMConfig(
                provider=LLMProvider.CLAUDE,
                model="claude-sonnet-4-5-20250929"
            ),
            data_config=DataConfig(
                data_mode=DataMode.NEW,
                sections=[1, 2, 3]
            ),
            prompts=PromptTemplates(
                paid="Generate article for e2e test"
            )
        )
        await mongodb_client.trigger_prompts.insert_one(
            config.model_dump(by_alias=True)
        )

        # Step 2: Publish configuration (isActive=true, create version)
        await mongodb_client.trigger_prompts.update_one(
            {"trigger_name": "e2e_test"},
            {
                "$set": {
                    "isActive": True,
                    "published_at": datetime.now(datetime.UTC),
                    "published_by": "admin@example.com"
                },
                "$inc": {"version": 1}
            }
        )

        # Create version snapshot
        config_doc = await mongodb_client.trigger_prompts.find_one(
            {"trigger_name": "e2e_test"}
        )
        version = PromptVersion(
            trigger_name="e2e_test",
            version=config_doc["version"],
            llm_config=config_doc["llm_config"],
            data_config=config_doc["data_config"],
            prompts=config_doc["prompts"],
            published_by="admin@example.com"
        )
        await mongodb_client.prompt_versions.insert_one(
            version.model_dump(by_alias=True)
        )

        # Step 3: Generate news (simulated)
        history = GenerationHistory(
            trigger_name="e2e_test",
            stockid=99999,
            prompt_type="paid",
            data_mode="new",
            model="claude-sonnet-4-5-20250929",
            input_data={"section_1": {"data": "test"}},
            prompt_used="Generate article for e2e test",
            generated_html="<article>E2E Test Content</article>",
            extracted_title="E2E Test Article",
            extracted_summary="This is an end-to-end test",
            extracted_article="<p>Full article content</p>",
            method="new",
            tokens_used=5000,
            cost=0.15,
            generation_time=2.5,
            status="success"
        )
        await mongodb_client.generation_history.insert_one(
            history.model_dump(by_alias=True)
        )

        # Verify workflow
        final_config = await mongodb_client.trigger_prompts.find_one(
            {"trigger_name": "e2e_test"}
        )
        assert final_config["isActive"] is True
        assert final_config["version"] == 2

        version_doc = await mongodb_client.prompt_versions.find_one(
            {"trigger_name": "e2e_test", "version": 2}
        )
        assert version_doc is not None

        history_doc = await mongodb_client.generation_history.find_one(
            {"trigger_name": "e2e_test", "stockid": 99999}
        )
        assert history_doc is not None
        assert history_doc["status"] == "success"
