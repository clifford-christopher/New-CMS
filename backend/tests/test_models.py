"""
Unit tests for Pydantic model validation
"""
import pytest
from app.models import NewsTrigger, TriggerPrompt, Configuration, User, AuditLog
from app.models import PromptVariant, ModelConfig, SpecialHandling, PromptMetadata, PromptStats, PromptConfig
from datetime import datetime


def test_news_trigger_model_validation():
    """Test NewsTrigger model with valid data"""
    trigger = NewsTrigger(
        _id="test_trigger_001",
        stockid=107182,
        comp_name="Test Company Ltd",
        sector="Technology",
        industry="Software",
        date_time_trigger="2023-12-08 20:31:09",
        trigger_name=["price_movement"],
        date="2023-12-08",
        status=1,
        category=["volatility"],
        data="Market data analysis",
        types_of_trigger=["technical"],
        result="2023-10-31",
        result_quarter=202309,
        upcoming_result=None,
        scoreText="Buy",
        score=72,
        scoreTxtChngDate="2023-12-04",
        prevScoreText="Strong Buy",
        mcapsizerank="midcap",
        trigger_date="2023-12-08",
        mcap_grade=2,
        stock_1y_return="42.32",
        sensex_1y_return="11.59",
        turn_arround="No"
    )
    assert trigger.id == "test_trigger_001"
    assert trigger.stockid == 107182
    assert trigger.comp_name == "Test Company Ltd"


def test_prompt_variant_model():
    """Test PromptVariant model"""
    variant = PromptVariant(
        article="Generate a news article about...",
        system=None
    )
    assert variant.article == "Generate a news article about..."
    assert variant.system is None


def test_model_config():
    """Test ModelConfig model"""
    config = ModelConfig(
        model_name="gpt-4o-mini",
        provider="openai",
        temperature=0.1,
        max_tokens=2000,
        cost_per_1m_input_tokens=0.15,
        cost_per_1m_output_tokens=0.6
    )
    assert config.model_name == "gpt-4o-mini"
    assert config.provider == "openai"
    assert config.temperature == 0.1


def test_trigger_prompt_model():
    """Test TriggerPrompt model with valid data"""
    prompt = TriggerPrompt(
        _id="prompt_001",
        trigger_name="52_week_high_summary",
        trigger_key="52_week_high_summary",
        trigger_display_name="52 Week High Summary",
        model_config=ModelConfig(
            model_name="gpt-4o-mini",
            provider="openai",
            temperature=0.1,
            max_tokens=2000,
            cost_per_1m_input_tokens=0.15,
            cost_per_1m_output_tokens=0.6
        ),
        prompts={
            "paid": PromptVariant(article="Paid article prompt", system=None),
            "unpaid": PromptVariant(article="Unpaid article prompt", system=None),
            "crawler": PromptVariant(article="Crawler article prompt", system=None)
        },
        special_handling=SpecialHandling(
            has_irb_boilerplate=False,
            irb_stock_id=None,
            irb_boilerplate_text=None,
            irb_unpaid_override=None,
            irb_crawler_override=None
        ),
        metadata=PromptMetadata(
            created_at="2025-10-29 10:00:04.117000",
            updated_at="2025-10-29 10:00:04.117000",
            version=1,
            extracted_from="generate_news.py",
            extraction_date="2025-10-29 10:00:04.117000",
            notes="Test prompt",
            cms_managed=False
        ),
        stats=PromptStats(
            total_generations=0,
            last_used=None,
            avg_generation_time_ms=None,
            success_rate=None
        )
    )
    assert prompt.id == "prompt_001"
    assert prompt.trigger_key == "52_week_high_summary"
    assert prompt.model_config_data.model_name == "gpt-4o-mini"


def test_configuration_model():
    """Test Configuration model with valid data"""
    config = Configuration(
        _id="config_001",
        trigger_key="test_trigger",
        trigger_name="Test Trigger",
        trigger_display_name="Test Trigger Display",
        version=1,
        model_config={"model_name": "gpt-4o-mini", "temperature": 0.7},
        prompts={
            "paid": PromptConfig(
                article="Test article prompt",
                system=None,
                version_history=[],
                last_test_generation=None
            )
        },
        special_handling=None,
        created_by="test_user",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        published_at=None,
        is_active=True,
        cms_managed=True
    )
    assert config.id == "config_001"
    assert config.trigger_key == "test_trigger"
    assert config.version == 1
    assert config.is_active is True
    assert config.cms_managed is True


def test_user_model():
    """Test User model with valid data"""
    user = User(
        _id="user_001",
        username="testuser",
        email="test@example.com",
        role="content_manager",
        created_at=datetime.utcnow()
    )
    assert user.id == "user_001"
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "content_manager"


def test_audit_log_model():
    """Test AuditLog model with valid data"""
    log = AuditLog(
        _id="log_001",
        user_id="user_001",
        action="prompt_edited",
        trigger_key="test_trigger",
        timestamp=datetime.utcnow(),
        details={"field_changed": "article", "old_value": "old", "new_value": "new"}
    )
    assert log.id == "log_001"
    assert log.user_id == "user_001"
    assert log.action == "prompt_edited"
    assert log.trigger_key == "test_trigger"
    assert isinstance(log.details, dict)
