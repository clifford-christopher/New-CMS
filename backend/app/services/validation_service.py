"""
Validation Service for Configuration Publishing
Story 5.1: Pre-Publish Validation

Validates that a trigger configuration is ready for production publishing.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase


class ValidationIssue(BaseModel):
    """Represents a single validation issue"""
    severity: str  # 'error', 'warning'
    category: str  # 'prompt', 'api', 'section', 'model', 'test'
    message: str
    prompt_type: Optional[str] = None  # 'paid', 'unpaid', 'crawler', or None for shared config


class PromptTypeValidation(BaseModel):
    """Validation results for a single prompt type"""
    prompt_type: str
    is_valid: bool
    issues: List[ValidationIssue] = []
    test_metadata: Optional[Dict[str, Any]] = None  # Models tested, cost, latency


class ValidationResult(BaseModel):
    """Complete validation result for a trigger configuration"""
    is_valid: bool
    prompt_types: Dict[str, PromptTypeValidation]  # Keyed by prompt_type
    shared_config_issues: List[ValidationIssue] = []
    summary: Dict[str, int]  # Total errors, warnings


class ConfigurationValidationService:
    """
    Service for validating trigger configurations before publishing
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.generation_history = db.generation_history
        self.triggers = db.triggers

    async def validate_configuration(
        self,
        trigger_id: str,
        apis: List[str],
        section_order: List[str],
        prompts: Dict[str, str],  # {prompt_type: prompt_template}
        model_settings: Dict[str, Any],
        enabled_prompt_types: List[str],
        session_id: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate complete trigger configuration

        Args:
            trigger_id: Trigger identifier
            apis: List of configured API identifiers
            section_order: Ordered list of section IDs
            prompts: Dict of prompt templates by type
            model_settings: Model configuration (temperature, max_tokens, selected_models)
            enabled_prompt_types: List of enabled prompt types to validate
            session_id: Optional session ID to check for recent tests

        Returns:
            ValidationResult with all validation checks
        """

        prompt_type_results: Dict[str, PromptTypeValidation] = {}
        shared_issues: List[ValidationIssue] = []

        # Validate shared configuration
        shared_issues.extend(self._validate_apis(apis))
        shared_issues.extend(self._validate_section_order(section_order))
        shared_issues.extend(self._validate_model_settings(model_settings))

        # Validate each enabled prompt type
        for prompt_type in enabled_prompt_types:
            prompt_template = prompts.get(prompt_type, "")

            # Validate prompt template
            prompt_issues = self._validate_prompt_template(prompt_type, prompt_template)

            # Validate test generation results
            test_issues, test_metadata = await self._validate_test_results(
                trigger_id,
                prompt_type,
                model_settings.get("selected_models", []),
                session_id
            )

            all_issues = prompt_issues + test_issues
            has_errors = any(issue.severity == 'error' for issue in all_issues)

            prompt_type_results[prompt_type] = PromptTypeValidation(
                prompt_type=prompt_type,
                is_valid=not has_errors,
                issues=all_issues,
                test_metadata=test_metadata
            )

        # Calculate summary
        total_errors = sum(
            len([i for i in result.issues if i.severity == 'error'])
            for result in prompt_type_results.values()
        )
        total_errors += len([i for i in shared_issues if i.severity == 'error'])

        total_warnings = sum(
            len([i for i in result.issues if i.severity == 'warning'])
            for result in prompt_type_results.values()
        )
        total_warnings += len([i for i in shared_issues if i.severity == 'warning'])

        is_valid = total_errors == 0

        return ValidationResult(
            is_valid=is_valid,
            prompt_types=prompt_type_results,
            shared_config_issues=shared_issues,
            summary={
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "prompt_types_validated": len(enabled_prompt_types)
            }
        )

    def _validate_apis(self, apis: List[str]) -> List[ValidationIssue]:
        """Validate API configuration"""
        issues = []

        if not apis or len(apis) == 0:
            issues.append(ValidationIssue(
                severity='error',
                category='api',
                message='At least one data API must be configured'
            ))

        return issues

    def _validate_section_order(self, section_order: List[str]) -> List[ValidationIssue]:
        """Validate section ordering"""
        issues = []

        if not section_order or len(section_order) == 0:
            issues.append(ValidationIssue(
                severity='error',
                category='section',
                message='Section order must be defined'
            ))

        return issues

    def _validate_model_settings(self, model_settings: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate model configuration"""
        issues = []

        selected_models = model_settings.get("selected_models", [])
        if not selected_models or len(selected_models) == 0:
            issues.append(ValidationIssue(
                severity='error',
                category='model',
                message='At least one model must be selected for testing'
            ))

        temperature = model_settings.get("temperature")
        if temperature is not None and (temperature < 0.0 or temperature > 1.0):
            issues.append(ValidationIssue(
                severity='error',
                category='model',
                message=f'Temperature must be between 0.0 and 1.0 (got {temperature})'
            ))

        max_tokens = model_settings.get("max_tokens")
        if max_tokens is not None and max_tokens < 1:
            issues.append(ValidationIssue(
                severity='error',
                category='model',
                message=f'Max tokens must be positive (got {max_tokens})'
            ))

        return issues

    def _validate_prompt_template(self, prompt_type: str, prompt_template: str) -> List[ValidationIssue]:
        """Validate prompt template for a specific type"""
        issues = []

        if not prompt_template or prompt_template.strip() == "":
            issues.append(ValidationIssue(
                severity='error',
                category='prompt',
                message=f'Prompt template is empty',
                prompt_type=prompt_type
            ))
            return issues

        # Check for placeholders
        import re
        section_pattern = r'\{\{[a-zA-Z_][a-zA-Z0-9_\s]*\}\}'
        data_pattern = r'\{data\.[a-zA-Z_][a-zA-Z0-9_.]*\}'

        has_section_placeholder = bool(re.search(section_pattern, prompt_template))
        has_data_placeholder = bool(re.search(data_pattern, prompt_template))

        if not (has_section_placeholder or has_data_placeholder):
            issues.append(ValidationIssue(
                severity='warning',
                category='prompt',
                message='No placeholders detected - prompt may not use configured data',
                prompt_type=prompt_type
            ))

        # Check prompt length
        if len(prompt_template) < 50:
            issues.append(ValidationIssue(
                severity='warning',
                category='prompt',
                message=f'Prompt template is very short ({len(prompt_template)} chars) - consider adding more detail',
                prompt_type=prompt_type
            ))

        return issues

    async def _validate_test_results(
        self,
        trigger_id: str,
        prompt_type: str,
        selected_models: List[str],
        session_id: Optional[str] = None
    ) -> tuple[List[ValidationIssue], Optional[Dict[str, Any]]]:
        """
        Validate that test generation results exist and are successful

        Returns:
            Tuple of (issues, test_metadata)
        """
        issues = []
        test_metadata = None

        # Build query for recent test results
        query = {
            "prompt_type": prompt_type
        }

        # If session_id provided, use it; otherwise look for tests in last 24 hours
        if session_id:
            query["session_id"] = session_id
        else:
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            query["timestamp"] = {"$gte": cutoff_time}

        # Find test results
        test_results = await self.generation_history.find(query).to_list(length=100)

        if not test_results:
            issues.append(ValidationIssue(
                severity='error',
                category='test',
                message='No test generation found - please run tests before publishing',
                prompt_type=prompt_type
            ))
            return issues, None

        # Check for successful completions
        completed_results = [r for r in test_results if r.get("status") == "completed"]

        if not completed_results:
            issues.append(ValidationIssue(
                severity='error',
                category='test',
                message=f'No successful test generations found ({len(test_results)} tests failed)',
                prompt_type=prompt_type
            ))
            return issues, None

        # Check that all selected models were tested
        tested_models = set(r.get("model_name", "") for r in completed_results)
        missing_models = set(selected_models) - tested_models

        if missing_models:
            issues.append(ValidationIssue(
                severity='warning',
                category='test',
                message=f'Not all selected models were tested: {", ".join(missing_models)}',
                prompt_type=prompt_type
            ))

        # Validate generation quality
        for result in completed_results:
            generated_text = result.get("generated_text", "")
            if not generated_text or generated_text.strip() == "":
                issues.append(ValidationIssue(
                    severity='error',
                    category='test',
                    message=f'Test generation for {result.get("model_name")} produced empty output',
                    prompt_type=prompt_type
                ))

        # Check for high costs (warning only)
        avg_cost = sum(r.get("cost", 0) for r in completed_results) / len(completed_results)
        if avg_cost > 0.50:  # More than $0.50 per generation
            issues.append(ValidationIssue(
                severity='warning',
                category='test',
                message=f'High average cost detected: ${avg_cost:.2f} per generation',
                prompt_type=prompt_type
            ))

        # Check for slow generations (warning only)
        avg_latency = sum(r.get("latency", 0) for r in completed_results) / len(completed_results)
        if avg_latency > 30:  # More than 30 seconds
            issues.append(ValidationIssue(
                severity='warning',
                category='test',
                message=f'Slow average latency detected: {avg_latency:.1f}s per generation',
                prompt_type=prompt_type
            ))

        # Build test metadata
        test_metadata = {
            "models_tested": list(tested_models),
            "total_tests": len(completed_results),
            "avg_cost": round(avg_cost, 4),
            "avg_latency": round(avg_latency, 2),
            "total_cost": round(sum(r.get("cost", 0) for r in completed_results), 4),
            "sample_output": completed_results[0].get("generated_text", "")[:200] + "..."  # First 200 chars
        }

        return issues, test_metadata


# Singleton instance
_validation_service: Optional[ConfigurationValidationService] = None


def get_validation_service(db: AsyncIOMotorDatabase) -> ConfigurationValidationService:
    """Get or create validation service instance"""
    global _validation_service
    if _validation_service is None:
        _validation_service = ConfigurationValidationService(db)
    return _validation_service
