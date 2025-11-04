"""
Unit tests for TriggerPromptConfig and related models.
Tests validation rules, backward compatibility, and enum values.
"""
import pytest
from datetime import datetime
from app.models.trigger_prompt_config import (
    TriggerPromptConfig,
    DataConfig,
    LLMConfig,
    PromptTemplates,
    DataMode,
    LLMProvider
)


class TestDataConfig:
    """Tests for DataConfig model and validation rules."""

    def test_valid_data_config(self):
        """Test valid DataConfig creation."""
        config = DataConfig(
            data_mode=DataMode.NEW,
            sections=[1, 2, 3, 5, 7],
            section_order=[1, 2, 3, 5, 7]
        )
        assert config.data_mode == DataMode.NEW
        assert config.sections == [1, 2, 3, 5, 7]

    def test_sections_must_be_1_to_14(self):
        """Test sections must be integers between 1 and 14."""
        with pytest.raises(ValueError, match="between 1 and 14"):
            DataConfig(
                data_mode=DataMode.NEW,
                sections=[0, 1, 15]  # 0 and 15 are out of range
            )

    def test_sections_no_duplicates(self):
        """Test sections must not have duplicates."""
        with pytest.raises(ValueError, match="must not contain duplicates"):
            DataConfig(
                data_mode=DataMode.NEW,
                sections=[1, 1, 2, 3]  # Duplicate 1
            )

    def test_section_order_must_match_sections(self):
        """Test section_order must contain same values as sections."""
        with pytest.raises(ValueError, match="must contain same values"):
            DataConfig(
                data_mode=DataMode.NEW,
                sections=[1, 2, 3],
                section_order=[1, 2]  # Missing 3
            )

    def test_section_order_different_order_valid(self):
        """Test section_order can be in different order than sections."""
        config = DataConfig(
            data_mode=DataMode.NEW,
            sections=[1, 3, 2],
            section_order=[1, 2, 3]  # Different order but same values
        )
        assert config.section_order == [1, 2, 3]

    def test_sections_optional(self):
        """Test sections and section_order are optional."""
        config = DataConfig(data_mode=DataMode.OLD)
        assert config.sections is None
        assert config.section_order is None


class TestLLMConfig:
    """Tests for LLMConfig model."""

    def test_valid_llm_config_claude(self):
        """Test valid LLMConfig with Claude provider."""
        config = LLMConfig(
            provider=LLMProvider.CLAUDE,
            model="claude-sonnet-4-5-20250929",
            temperature=0.7,
            max_tokens=20000
        )
        assert config.provider == LLMProvider.CLAUDE
        assert config.model == "claude-sonnet-4-5-20250929"

    def test_valid_llm_config_openai(self):
        """Test valid LLMConfig with OpenAI provider."""
        config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
            temperature=0.5,
            max_tokens=15000
        )
        assert config.provider == LLMProvider.OPENAI
        assert config.model == "gpt-4o"

    def test_temperature_validation(self):
        """Test temperature must be between 0.0 and 1.0."""
        # Valid temperatures
        LLMConfig(provider=LLMProvider.CLAUDE, model="test", temperature=0.0)
        LLMConfig(provider=LLMProvider.CLAUDE, model="test", temperature=1.0)

        # Invalid temperatures
        with pytest.raises(ValueError):
            LLMConfig(provider=LLMProvider.CLAUDE, model="test", temperature=-0.1)
        with pytest.raises(ValueError):
            LLMConfig(provider=LLMProvider.CLAUDE, model="test", temperature=1.1)

    def test_max_tokens_must_be_positive(self):
        """Test max_tokens must be greater than 0."""
        with pytest.raises(ValueError):
            LLMConfig(
                provider=LLMProvider.CLAUDE,
                model="test",
                max_tokens=0
            )

    def test_default_values(self):
        """Test default values for temperature and max_tokens."""
        config = LLMConfig(
            provider=LLMProvider.CLAUDE,
            model="test"
        )
        assert config.temperature == 0.7
        assert config.max_tokens == 20000


class TestPromptTemplates:
    """Tests for PromptTemplates model."""

    def test_paid_prompt_required(self):
        """Test paid prompt is required."""
        with pytest.raises(ValueError):
            PromptTemplates()  # Missing paid

    def test_paid_prompt_cannot_be_empty(self):
        """Test paid prompt cannot be empty string."""
        with pytest.raises(ValueError):
            PromptTemplates(paid="")  # Empty string

    def test_unpaid_and_crawler_optional(self):
        """Test unpaid and crawler are optional."""
        prompts = PromptTemplates(paid="Generate article...")
        assert prompts.paid == "Generate article..."
        assert prompts.unpaid is None
        assert prompts.crawler is None

    def test_all_three_prompts(self):
        """Test all three prompt types can be provided."""
        prompts = PromptTemplates(
            paid="Paid article...",
            unpaid="Unpaid summary...",
            crawler="SEO content..."
        )
        assert prompts.paid == "Paid article..."
        assert prompts.unpaid == "Unpaid summary..."
        assert prompts.crawler == "SEO content..."


class TestTriggerPromptConfig:
    """Tests for TriggerPromptConfig model."""

    def test_valid_trigger_prompt_config(self):
        """Test valid TriggerPromptConfig creation."""
        config = TriggerPromptConfig(
            trigger_name="earnings_result",
            isActive=True,
            llm_config=LLMConfig(
                provider=LLMProvider.CLAUDE,
                model="claude-sonnet-4-5-20250929"
            ),
            data_config=DataConfig(
                data_mode=DataMode.NEW,
                sections=[1, 2, 3],
                section_order=[1, 2, 3]
            ),
            prompts=PromptTemplates(
                paid="Generate article...",
                unpaid="Generate summary..."
            )
        )
        assert config.trigger_name == "earnings_result"
        assert config.isActive is True

    def test_backward_compatibility_defaults(self):
        """Test existing documents without new fields use default values."""
        # Simulate existing document without new fields
        existing_doc = {
            "trigger_name": "earnings_result"
            # No isActive, llm_config, data_config, prompts fields
        }
        config = TriggerPromptConfig(**existing_doc)

        # Should use default values
        assert config.isActive is False  # Default for legacy workflow
        assert config.llm_config is None
        assert config.data_config is None
        assert config.prompts is None
        assert config.version == 1

    def test_isActive_false_means_legacy_workflow(self):
        """Test isActive=false indicates legacy generation method."""
        config = TriggerPromptConfig(
            trigger_name="test_trigger",
            isActive=False
        )
        # This would trigger legacy generation method in NewsGenerationService
        assert config.isActive is False

    def test_version_defaults_to_1(self):
        """Test version defaults to 1."""
        config = TriggerPromptConfig(trigger_name="test")
        assert config.version == 1

    def test_timestamps_auto_populated(self):
        """Test created_at and updated_at are auto-populated."""
        config = TriggerPromptConfig(trigger_name="test")
        assert isinstance(config.created_at, datetime)
        assert isinstance(config.updated_at, datetime)

    def test_published_metadata_optional(self):
        """Test published_at and published_by are optional."""
        config = TriggerPromptConfig(trigger_name="test")
        assert config.published_at is None
        assert config.published_by is None


class TestEnums:
    """Tests for enum values."""

    def test_data_mode_enum_values(self):
        """Test DataMode enum values."""
        assert DataMode.OLD == "old"
        assert DataMode.NEW == "new"
        assert DataMode.OLD_NEW == "old_new"

    def test_llm_provider_enum_values(self):
        """Test LLMProvider enum values (Google removed)."""
        assert LLMProvider.OPENAI == "openai"
        assert LLMProvider.CLAUDE == "claude"
        # No GOOGLE - removed per requirements

    def test_invalid_data_mode_rejected(self):
        """Test invalid data_mode value is rejected."""
        with pytest.raises(ValueError):
            DataConfig(data_mode="invalid")  # type: ignore
