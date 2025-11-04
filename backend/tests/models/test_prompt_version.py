"""
Unit tests for PromptVersion model.
Tests version history tracking and rollback capability.
"""
import pytest
from datetime import datetime
from app.models.prompt_version import PromptVersion


class TestPromptVersion:
    """Tests for PromptVersion model."""

    def test_valid_prompt_version(self):
        """Test valid PromptVersion creation."""
        version = PromptVersion(
            trigger_name="earnings_result",
            version=3,
            llm_config={
                "provider": "claude",
                "model": "claude-sonnet-4-5-20250929",
                "temperature": 0.7,
                "max_tokens": 20000
            },
            data_config={
                "data_mode": "new",
                "sections": [1, 2, 3, 5, 7],
                "section_order": [1, 2, 3, 5, 7]
            },
            prompts={
                "paid": "Generate article...",
                "unpaid": "Generate summary...",
                "crawler": "Generate SEO content..."
            },
            published_by="admin@example.com"
        )
        assert version.trigger_name == "earnings_result"
        assert version.version == 3
        assert version.published_by == "admin@example.com"

    def test_full_snapshot_preservation(self):
        """Test full configuration snapshot is preserved."""
        llm_snapshot = {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_tokens": 15000
        }
        data_snapshot = {
            "data_mode": "old_new",
            "sections": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            "section_order": [1, 3, 5, 7, 9, 11, 13, 2, 4, 6, 8, 10, 12, 14]
        }
        prompts_snapshot = {
            "paid": "Paid prompt template with {variables}",
            "unpaid": "Unpaid summary template",
            "crawler": None  # Can be None
        }

        version = PromptVersion(
            trigger_name="test",
            version=1,
            llm_config=llm_snapshot,
            data_config=data_snapshot,
            prompts=prompts_snapshot,
            published_by="editor@example.com"
        )

        # Verify exact snapshot preservation
        assert version.llm_config == llm_snapshot
        assert version.data_config == data_snapshot
        assert version.prompts == prompts_snapshot
        assert version.prompts["paid"] == "Paid prompt template with {variables}"
        assert version.prompts["crawler"] is None

    def test_published_at_auto_populated(self):
        """Test published_at is auto-populated."""
        version = PromptVersion(
            trigger_name="test",
            version=1,
            llm_config={},
            data_config={},
            prompts={},
            published_by="user@example.com"
        )
        assert isinstance(version.published_at, datetime)

    def test_usage_statistics_optional(self):
        """Test usage statistics are optional with defaults."""
        version = PromptVersion(
            trigger_name="test",
            version=1,
            llm_config={},
            data_config={},
            prompts={},
            published_by="user@example.com"
        )
        assert version.test_generation_count == 0
        assert version.avg_cost_per_generation == 0.0
        assert version.iteration_count == 0

    def test_usage_statistics_from_preview(self):
        """Test usage statistics can be recorded from preview phase."""
        version = PromptVersion(
            trigger_name="earnings_result",
            version=5,
            llm_config={},
            data_config={},
            prompts={},
            published_by="editor@example.com",
            test_generation_count=25,  # 25 preview generations
            avg_cost_per_generation=0.35,  # $0.35 per generation
            iteration_count=8  # 8 iterations of edits
        )
        assert version.test_generation_count == 25
        assert version.avg_cost_per_generation == 0.35
        assert version.iteration_count == 8

        # Calculate total preview cost
        total_preview_cost = version.test_generation_count * version.avg_cost_per_generation
        assert total_preview_cost == 8.75  # $8.75 spent on preview testing

    def test_version_number_increments(self):
        """Test version numbers increment correctly."""
        versions = []
        for v in range(1, 6):
            version = PromptVersion(
                trigger_name="test",
                version=v,
                llm_config={},
                data_config={},
                prompts={},
                published_by="user@example.com"
            )
            versions.append(version)

        assert versions[0].version == 1
        assert versions[1].version == 2
        assert versions[4].version == 5

    def test_rollback_use_case(self):
        """Test rollback scenario - retrieve version 2 when version 3 has issues."""
        # Version 2 (working configuration)
        v2 = PromptVersion(
            trigger_name="earnings_result",
            version=2,
            llm_config={
                "provider": "claude",
                "model": "claude-sonnet-4-5-20250929",
                "temperature": 0.7,
                "max_tokens": 20000
            },
            data_config={
                "data_mode": "new",
                "sections": [1, 2, 3],
                "section_order": [1, 2, 3]
            },
            prompts={
                "paid": "Working prompt template"
            },
            published_by="editor1@example.com"
        )

        # Version 3 (broken configuration - wrong temperature)
        v3 = PromptVersion(
            trigger_name="earnings_result",
            version=3,
            llm_config={
                "provider": "claude",
                "model": "claude-sonnet-4-5-20250929",
                "temperature": 1.5,  # Invalid! But stored as-is for history
                "max_tokens": 20000
            },
            data_config={
                "data_mode": "new",
                "sections": [1, 2, 3],
                "section_order": [1, 2, 3]
            },
            prompts={
                "paid": "Broken prompt with typo"
            },
            published_by="editor2@example.com"
        )

        # Rollback: Use v2's configuration to restore working state
        assert v2.llm_config["temperature"] == 0.7
        assert v2.prompts["paid"] == "Working prompt template"
        assert v3.llm_config["temperature"] == 1.5  # Stored as-is for audit

    def test_audit_trail(self):
        """Test audit trail capability - who published what and when."""
        v1 = PromptVersion(
            trigger_name="test",
            version=1,
            llm_config={},
            data_config={},
            prompts={"paid": "Version 1 prompt"},
            published_by="alice@example.com"
        )

        v2 = PromptVersion(
            trigger_name="test",
            version=2,
            llm_config={},
            data_config={},
            prompts={"paid": "Version 2 prompt - updated by Bob"},
            published_by="bob@example.com"
        )

        v3 = PromptVersion(
            trigger_name="test",
            version=3,
            llm_config={},
            data_config={},
            prompts={"paid": "Version 3 prompt - updated by Alice again"},
            published_by="alice@example.com"
        )

        # Audit trail shows who made each change
        assert v1.published_by == "alice@example.com"
        assert v2.published_by == "bob@example.com"
        assert v3.published_by == "alice@example.com"

        # Can track what changed between versions
        assert v1.prompts["paid"] != v2.prompts["paid"]
        assert v2.prompts["paid"] != v3.prompts["paid"]

    def test_compare_versions_for_debugging(self):
        """Test version comparison for debugging what changed."""
        v1 = PromptVersion(
            trigger_name="earnings_result",
            version=1,
            llm_config={
                "provider": "openai",
                "model": "gpt-4o",
                "temperature": 0.7
            },
            data_config={
                "data_mode": "old",
                "sections": None
            },
            prompts={
                "paid": "Original prompt"
            },
            published_by="user1@example.com"
        )

        v2 = PromptVersion(
            trigger_name="earnings_result",
            version=2,
            llm_config={
                "provider": "claude",  # Changed provider
                "model": "claude-sonnet-4-5-20250929",  # Changed model
                "temperature": 0.7
            },
            data_config={
                "data_mode": "new",  # Changed data mode
                "sections": [1, 2, 3],  # Added sections
                "section_order": [1, 2, 3]
            },
            prompts={
                "paid": "Updated prompt with new instructions"  # Changed prompt
            },
            published_by="user2@example.com"
        )

        # Can compare and identify changes
        assert v1.llm_config["provider"] != v2.llm_config["provider"]
        assert v1.data_config["data_mode"] != v2.data_config["data_mode"]
        assert v1.prompts["paid"] != v2.prompts["paid"]
        assert v1.published_by != v2.published_by

    def test_empty_prompts_allowed_for_storage(self):
        """Test empty prompts dict is allowed (for storage/historical purposes)."""
        version = PromptVersion(
            trigger_name="test",
            version=1,
            llm_config={},
            data_config={},
            prompts={},  # Empty is valid for version storage
            published_by="user@example.com"
        )
        assert version.prompts == {}
