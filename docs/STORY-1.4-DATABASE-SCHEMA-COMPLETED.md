# Story 1.4: Database Schema Updates - COMPLETED

**Status:** ✅ DONE
**Completion Date:** 2025-10-30
**Version:** 2.0 (News CMS Workflow)

## Summary

Story 1.4 Database Schema Updates has been successfully implemented with complete Pydantic models, validation rules, migration scripts, and comprehensive test coverage.

## Files Created

### 1. Models (`backend/app/models/`)

#### `trigger_prompt_config.py` (115 lines)
- **TriggerPromptConfig**: Main model for trigger configurations
  - `isActive`: Critical flag controlling NEW vs LEGACY workflow routing
  - `llm_config`: LLM configuration (provider, model, temperature, max_tokens)
  - `data_config`: Data source configuration (data_mode, sections, section_order)
  - `prompts`: Multi-type prompt templates (paid required, unpaid/crawler optional)
  - Backward compatibility via Pydantic defaults
- **LLMConfig**: LLM model configuration with validation
  - Providers: OpenAI, Claude (Google removed per requirements)
  - Temperature: 0.0-1.0, default 0.7
  - Max tokens: >0, default 20000
- **DataConfig**: Data source configuration with validation
  - Sections: 1-14, no duplicates
  - section_order must match sections
- **PromptTemplates**: Multi-type prompt templates
  - paid: required, min_length=1
  - unpaid, crawler: optional
- **Enums**: LLMProvider, DataMode

#### `generation_history.py` (71 lines)
- **GenerationHistory**: Tracks all news generation attempts
  - Purpose: Analytics, debugging, A/B testing, cost tracking
  - Input data: merged data, prompt used
  - Output: generated HTML, extracted title/summary/article
  - Metadata: method (new/legacy), tokens, cost, generation time, status

#### `prompt_version.py` (65 lines)
- **PromptVersion**: Version history for rollback capability
  - Purpose: Rollback, audit trail, debugging
  - Full snapshot: llm_config, data_config, prompts
  - Audit metadata: published_at, published_by
  - Usage statistics: test_generation_count, avg_cost_per_generation

### 2. Migration Scripts (`backend/scripts/`)

#### `create_workflow_indexes.py` (135 lines)
- Creates MongoDB indexes for all collections
- **trigger_prompts**: trigger_name (unique), isActive
- **generation_history**: compound (trigger_name+stockid+timestamp), prompt_type, status
- **prompt_versions**: compound (trigger_name+version)
- **structured_data_jobs**: job_id (unique), created_at (TTL: 24 hours)
- Usage: `python backend/scripts/create_workflow_indexes.py`

### 3. Unit Tests (`backend/tests/models/`)

#### `test_trigger_prompt_config.py` (246 lines)
- **TestDataConfig**: 6 tests for sections validation
- **TestLLMConfig**: 5 tests for LLM configuration
- **TestPromptTemplates**: 4 tests for prompt templates
- **TestTriggerPromptConfig**: 6 tests for main configuration
- **TestEnums**: 3 tests for enum values
- **Total**: 24 tests, 100% pass rate

#### `test_generation_history.py` (192 lines)
- **TestGenerationHistory**: 9 tests for generation tracking
- Tests: prompt types, data modes, methods, status, timestamps, cost tracking
- **Total**: 9 tests, 100% pass rate

#### `test_prompt_version.py` (283 lines)
- **TestPromptVersion**: 10 tests for version history
- Tests: snapshots, rollback, audit trail, version comparison
- **Total**: 10 tests, 100% pass rate

### 4. Integration Tests (`backend/tests/integration/`)

#### `test_database_schema.py` (529 lines)
- **TestTriggerPromptConfigIntegration**: 4 tests
- **TestGenerationHistoryIntegration**: 4 tests
- **TestPromptVersionIntegration**: 3 tests
- **TestEndToEndWorkflow**: 1 complete workflow test
- **Total**: 12 integration tests (requires MongoDB)

## Test Results

```
43 unit tests passed (100% coverage on models)
- test_trigger_prompt_config.py: 24 passed
- test_generation_history.py: 9 passed
- test_prompt_version.py: 10 passed

Model coverage: 100%
- trigger_prompt_config.py: 100%
- generation_history.py: 100%
- prompt_version.py: 100%
```

## Key Technical Decisions

### 1. Field Naming: `llm_config` vs `model_config`
**Issue**: Pydantic v2 reserves `model_config` for model configuration
**Solution**: Renamed to `llm_config` throughout all models and tests

### 2. Datetime UTC Compatibility
**Issue**: `datetime.UTC` not available in Python 3.13
**Solution**: Use `datetime.now(timezone.utc)` instead

### 3. Backward Compatibility
**Implementation**: Pydantic default values ensure existing documents work:
- `isActive=false` → triggers legacy workflow
- `llm_config=None` → no model configuration
- `data_config=None` → no data configuration
- `prompts=None` → no prompts

### 4. Google Provider Removal
**Requirement**: Remove Google provider from LLMProvider enum
**Implementation**: Only OpenAI and Claude providers supported

### 5. Validation Rules
**Sections**: Must be 1-14, no duplicates
**section_order**: Must contain same values as sections
**Temperature**: Must be 0.0-1.0
**Max tokens**: Must be >0
**Paid prompt**: Required, min_length=1

## MongoDB Collections Extended/Created

### Extended: `trigger_prompts`
- **New fields**: isActive, llm_config, data_config, prompts, version, timestamps
- **Indexes**: trigger_name (unique), isActive

### Created: `generation_history`
- **Purpose**: Track all news generation attempts
- **Indexes**: trigger_name+stockid+timestamp (compound), prompt_type, status, timestamp

### Created: `prompt_versions`
- **Purpose**: Version history for rollback
- **Indexes**: trigger_name+version (compound), published_at

### Created: `structured_data_jobs` (Story 2.4)
- **Purpose**: Async job tracking
- **Indexes**: job_id (unique), created_at (TTL: 24 hours)

## Dependencies

### Python Packages
- `pydantic>=2.0` - Data validation
- `motor` - Async MongoDB driver
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support

### Database
- MongoDB 4.4+ (for TTL indexes)

## Usage Examples

### Creating a TriggerPromptConfig
```python
from app.models.trigger_prompt_config import (
    TriggerPromptConfig, LLMConfig, DataConfig, PromptTemplates,
    LLMProvider, DataMode
)

config = TriggerPromptConfig(
    trigger_name="earnings_result",
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
        paid="Generate detailed article for {{company_name}}...",
        unpaid="Generate brief summary for {{company_name}}...",
        crawler="SEO content for {{company_name}}..."
    )
)
```

### Tracking Generation History
```python
from app.models.generation_history import GenerationHistory

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
```

### Creating Version Snapshot
```python
from app.models.prompt_version import PromptVersion

version = PromptVersion(
    trigger_name="earnings_result",
    version=3,
    llm_config=config.llm_config.model_dump(),
    data_config=config.data_config.model_dump(),
    prompts=config.prompts.model_dump(),
    published_by="admin@example.com",
    test_generation_count=10,
    avg_cost_per_generation=0.35
)
```

## Next Steps

### Story 1.4: Trigger Management Dashboard
**Status**: Ready to implement
**Dependencies**: Database schema (DONE)
**Files to create**:
- `backend/app/routers/triggers.py` (GET /api/triggers)
- `frontend/src/components/dashboard/TriggerCard.tsx`
- `frontend/src/components/dashboard/TriggerTable.tsx`
- `frontend/src/app/page.tsx` (update)

### Epic 2+ Stories
**Status**: Unblocked
All Epic 2+ stories now have required database schema in place:
- ✅ Story 2.3: Data Retrieval
- ✅ Story 2.4: Structured Data Generation
- ✅ Story 2.5: 14-Section Selection
- ✅ Story 3.2: Multi-Type Prompt Editor
- ✅ Story 4.1: Adaptive LLM Routing
- ✅ Story 4.3: Parallel News Generation
- ✅ Story 5.2: Configuration Publishing

## Acceptance Criteria Met

- ✅ AC 1.1: Extended trigger_prompts collection with new fields
- ✅ AC 1.2: isActive field with default false for backward compatibility
- ✅ AC 1.3: Pydantic models with validation
- ✅ AC 2.1: LLMConfig with provider enum (OpenAI, Claude - Google removed)
- ✅ AC 2.2: Temperature and max_tokens validation
- ✅ AC 3.1: DataConfig with data_mode enum
- ✅ AC 3.2: Sections validation (1-14, no duplicates)
- ✅ AC 3.3: section_order validation
- ✅ AC 4.1: PromptTemplates with paid required
- ✅ AC 5.1: generation_history collection model
- ✅ AC 6.1: prompt_versions collection model
- ✅ AC 7.1: Migration script with MongoDB indexes
- ✅ AC 7.2: Compound indexes for performance
- ✅ AC 7.3: TTL index on structured_data_jobs (24 hours)

## Notes

### Breaking Changes
**None** - Backward compatible via Pydantic defaults

### Migration Required
Run migration script to create indexes:
```bash
python backend/scripts/create_workflow_indexes.py
```

### Documentation Updates
- Story 1.4 Database Schema marked as DONE
- All Epic 2+ stories reference correct field names (llm_config)
- Integration tests document full workflow

## Contributors

- Claude Code (AI Assistant)
- Implementation Date: 2025-10-30
