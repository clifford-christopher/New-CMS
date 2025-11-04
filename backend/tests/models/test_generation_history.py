"""
Unit tests for GenerationHistory model.
Tests tracking of news generation attempts and metadata validation.
"""
import pytest
from datetime import datetime
from app.models.generation_history import GenerationHistory


class TestGenerationHistory:
    """Tests for GenerationHistory model."""

    def test_valid_generation_history(self):
        """Test valid GenerationHistory creation."""
        history = GenerationHistory(
            trigger_name="earnings_result",
            stockid=12345,
            prompt_type="paid",
            data_mode="new",
            model="claude-sonnet-4-5-20250929",
            input_data={"section_1": {"data": "value"}},
            prompt_used="Generate article based on...",
            generated_html="<article>Content</article>",
            extracted_title="Apple Earnings Beat Expectations",
            extracted_summary="Apple reported strong quarterly results...",
            extracted_article="<p>Apple Inc. today reported...</p>",
            method="new",
            tokens_used=15000,
            cost=0.45,
            generation_time=3.5,
            status="success"
        )
        assert history.trigger_name == "earnings_result"
        assert history.stockid == 12345
        assert history.prompt_type == "paid"
        assert history.method == "new"

    def test_prompt_type_values(self):
        """Test prompt_type accepts paid, unpaid, crawler."""
        for prompt_type in ["paid", "unpaid", "crawler"]:
            history = GenerationHistory(
                trigger_name="test",
                stockid=123,
                prompt_type=prompt_type,
                data_mode="new",
                model="test-model",
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
            assert history.prompt_type == prompt_type

    def test_data_mode_values(self):
        """Test data_mode accepts old, new, old_new."""
        for data_mode in ["old", "new", "old_new"]:
            history = GenerationHistory(
                trigger_name="test",
                stockid=123,
                prompt_type="paid",
                data_mode=data_mode,
                model="test-model",
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
            assert history.data_mode == data_mode

    def test_method_values(self):
        """Test method accepts new and legacy."""
        for method in ["new", "legacy"]:
            history = GenerationHistory(
                trigger_name="test",
                stockid=123,
                prompt_type="paid",
                data_mode="new",
                model="test-model",
                input_data={},
                prompt_used="test",
                generated_html="<html></html>",
                extracted_title="Title",
                extracted_summary="Summary",
                extracted_article="Article",
                method=method,
                tokens_used=100,
                cost=0.01,
                generation_time=1.0,
                status="success"
            )
            assert history.method == method

    def test_status_values(self):
        """Test status accepts success and failed."""
        # Success case
        history_success = GenerationHistory(
            trigger_name="test",
            stockid=123,
            prompt_type="paid",
            data_mode="new",
            model="test-model",
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
        assert history_success.status == "success"
        assert history_success.error_message is None

        # Failed case with error message
        history_failed = GenerationHistory(
            trigger_name="test",
            stockid=123,
            prompt_type="paid",
            data_mode="new",
            model="test-model",
            input_data={},
            prompt_used="test",
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
        assert history_failed.status == "failed"
        assert history_failed.error_message == "LLM API timeout after 30 seconds"

    def test_timestamp_auto_populated(self):
        """Test timestamp is auto-populated."""
        history = GenerationHistory(
            trigger_name="test",
            stockid=123,
            prompt_type="paid",
            data_mode="new",
            model="test-model",
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
        assert isinstance(history.timestamp, datetime)

    def test_cost_tracking_precision(self):
        """Test cost can store precise USD values."""
        history = GenerationHistory(
            trigger_name="test",
            stockid=123,
            prompt_type="paid",
            data_mode="new",
            model="gpt-4o",
            input_data={},
            prompt_used="test",
            generated_html="<html></html>",
            extracted_title="Title",
            extracted_summary="Summary",
            extracted_article="Article",
            method="new",
            tokens_used=25000,
            cost=0.12345,  # Precise cost
            generation_time=5.2,
            status="success"
        )
        assert history.cost == 0.12345
        assert history.tokens_used == 25000

    def test_input_data_complex_structure(self):
        """Test input_data can store complex nested structures."""
        complex_data = {
            "section_1": {
                "key_metrics": {"revenue": 123.4, "eps": 2.5},
                "narrative": "Company performance was strong..."
            },
            "section_2": {
                "tables": [
                    {"row": 1, "data": [1, 2, 3]},
                    {"row": 2, "data": [4, 5, 6]}
                ]
            },
            "old_data": {
                "headline": "Apple Reports Earnings"
            }
        }

        history = GenerationHistory(
            trigger_name="test",
            stockid=123,
            prompt_type="paid",
            data_mode="old_new",
            model="test-model",
            input_data=complex_data,
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
        assert history.input_data == complex_data
        assert history.input_data["section_1"]["key_metrics"]["revenue"] == 123.4

    def test_model_name_storage(self):
        """Test model names are stored correctly."""
        models = [
            "claude-sonnet-4-5-20250929",
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-5-sonnet-20241022"
        ]

        for model in models:
            history = GenerationHistory(
                trigger_name="test",
                stockid=123,
                prompt_type="paid",
                data_mode="new",
                model=model,
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
            assert history.model == model
