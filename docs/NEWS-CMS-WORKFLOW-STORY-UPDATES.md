# News CMS Workflow - Story Update Guide

## Overview

This document outlines the updates needed to existing stories (Epics 1-5) to incorporate the News CMS Workflow Feature requirements. Instead of creating new stories, we enhance existing ones with:

1. **stockid-specific APIs** (trigger_name + stockid required)
2. **Data modes** (OLD/NEW/OLD_NEW)
3. **Multi-type prompts** (paid/unpaid/crawler with tabbed interface)
4. **Adaptive generation** (isActive flag routing)
5. **No caching** for dynamic data

## Summary of Changes by Epic

| Epic | Stories to Update | Key Changes |
|------|-------------------|-------------|
| Epic 1 | 1.2, 1.4 | Extend trigger_prompts schema, add stockid to queries |
| Epic 2 | 2.3, 2.4, 2.5 | Replace generic API adapters with `generate_full_report.py`, add data modes |
| Epic 3 | 3.2, 3.3, 3.4 | Add multi-type prompts with tabbed interface, pre-population |
| Epic 4 | 4.1, 4.3, 4.4 | Add adaptive routing with isActive flag, remove Google provider |
| Epic 5 | 5.2, 5.5 | Update publish to set isActive=true, add version history |

---

## Epic 1: Foundation Updates

### Story 1.2: MongoDB Database Setup and Connection
**Status**: Done → **Update Required**

**Changes Needed**:
1. **Extend trigger_prompts collection** (AC: 2 - new)
   - Add new fields to seed data: isActive, model_config, data_config, prompts, version
   - Update Pydantic model to include new fields with defaults
   - Ensure backward compatibility (existing docs without new fields still work)

2. **Create new collections** (AC: 2 - new)
   - `generation_history` collection for preview/production tracking
   - `prompt_versions` collection for rollback capability

3. **Update indexes** (AC: 5 - new)
   - Add index on `trigger_prompts.isActive`
   - Add compound indexes on `generation_history` (trigger_name + stockid + timestamp)
   - Add index on `prompt_versions` (trigger_name + version)

**New Tasks**:
- [ ] Task 7: Extend trigger_prompts schema with News CMS Workflow fields
- [ ] Task 8: Create generation_history and prompt_versions collections
- [ ] Task 9: Create indexes for new fields and collections

**Updated Dev Notes**:
- Reference Story 1.4 (Database Schema Updates) for full Pydantic model definitions
- Migration script: `backend/scripts/create_indexes.py`

---

### Story 1.4: Trigger Management Dashboard
**Status**: Draft → **Update Required**

**Conflict**: There are TWO Story 1.4 files:
- `1.4.trigger-management-dashboard.md` (original from Epic 1)
- `1.4.database-schema-updates.md` (newly created for News CMS Workflow)

**Resolution**:
- **Rename** `1.4.trigger-management-dashboard.md` → `1.6.trigger-management-dashboard.md`
- **Keep** `1.4.database-schema-updates.md` as Story 1.4 (foundational for workflow)
- **Rename** `1.5.aws-deployment-setup.md` → `1.7.aws-deployment-setup.md`

**Changes to Trigger Management Dashboard** (now Story 1.6):
1. **Update trigger list display** (AC: 3 - modified)
   - Add "Workflow Status" column: Configured (has isActive=true), Draft (has config but isActive=false), Unconfigured
   - Add filter: Show only workflow-enabled triggers
   - Add "Configure Workflow" button per trigger

2. **Add stockid input to trigger selection** (AC: new)
   - When user clicks trigger, prompt for stockid input
   - Navigate to `/workflow/{trigger_name}?stockid={stockid}`
   - Store trigger_name + stockid in WorkflowContext

**New Acceptance Criteria**:
- 10. Trigger list shows workflow configuration status (Configured/Draft/Unconfigured)
- 11. "Configure Workflow" button navigates to News CMS Workflow pages
- 12. stockid input validation before navigation (positive integer required)

---

## Epic 2: Data Pipeline Updates

### Story 2.3: Data Retrieval and Raw JSON Display
**Status**: Draft → **Update Required**

**Major Changes**:

1. **Add stockid parameter** (AC: 2 - modified)
   - **OLD**: `POST /api/triggers/:id/data/fetch` with stock ID in body
   - **NEW**: `GET /api/triggers/{trigger_name}/data?stockid={stockid}`
   - Query MongoDB: `news_triggers.find_one({"trigger_name": [trigger_name], "stockid": stockid})`
   - Return existing OLD data from news_triggers collection

2. **Add data mode selection** (AC: new)
   - Radio buttons: OLD only | NEW only | OLD + NEW
   - If OLD: Show preview of existing data, skip section generation
   - If NEW or OLD_NEW: Enable "Generate Sections" button

3. **Remove generic API adapters** (AC: 2, 6 - modified)
   - **OLD**: Fetch from multiple financial data APIs
   - **NEW**: For NEW/OLD_NEW modes, call `POST /api/data/structured/generate` (Story 2.4)
   - For OLD mode, just display existing trigger data

4. **No caching** (AC: new)
   - Add note: "Data changes during market hours (9:15 AM - 3:30 PM IST)"
   - Set Cache-Control: no-cache headers

**Updated Acceptance Criteria**:
- 1. Data configuration page includes data mode radio buttons (OLD/NEW/OLD_NEW)
- 2. `GET /api/triggers/{trigger_name}/data?stockid={stockid}` fetches OLD data
- 3. stockid parameter is required (positive integer validation)
- 11. No caching for trigger data (always fresh from database)

**Removed Acceptance Criteria**:
- Old AC 2-6 (generic API adapter calls) - replaced with trigger data fetch + structured data generation

**New Dev Notes Section**:
```markdown
### Data Mode Logic

**OLD Mode**:
- Fetch: `GET /api/triggers/{trigger_name}/data?stockid={stockid}`
- Display: existing trigger data from news_triggers collection
- No section selection needed

**NEW Mode**:
- Generate: `POST /api/data/structured/generate` with stockid
- Display: 14 section checkboxes from generate_full_report.py
- Allow section selection and reordering

**OLD_NEW Mode**:
- Fetch OLD data + Generate NEW data
- Display: OLD data preview + 14 section checkboxes
- Merge happens at generation time (Story 4.3)
```

---

### Story 2.4: Parser Integration and Execution
**Status**: Draft → **Update Required**

**Major Changes**:

1. **Replace generic parser with generate_full_report.py** (AC: 1, 2 - modified)
   - **OLD**: Generic parser adapter for multiple data sources
   - **NEW**: Specific integration with `structured_report_builder/generate_full_report.py`
   - Subprocess execution: `python generate_full_report.py {stockid} {exchange}`
   - Parses 14 sections (separated by 80 "=" characters)

2. **Update endpoint** (AC: 3 - modified)
   - **OLD**: `POST /api/triggers/:id/data/parse` (accepts raw JSON)
   - **NEW**: `POST /api/data/structured/generate` (accepts stockid, sections, section_order)
   - Returns filtered and reordered sections based on user selection

3. **Add section filtering and reordering** (AC: new)
   - Accept `sections` parameter: array of integers 1-14
   - Accept `section_order` parameter: reordered sections
   - Filter parsed output to only include selected sections
   - Reorder sections based on section_order

4. **Increase timeout** (AC: 6 - modified)
   - **OLD**: 10 seconds default timeout
   - **NEW**: 60 seconds timeout (script takes 8-15 seconds for large reports)

5. **No caching** (AC: new)
   - Always generate fresh data (changes during market hours)
   - Document: "Structured data is time-sensitive, no caching"

**Updated Acceptance Criteria**:
- 1. `StructuredDataService` created for generate_full_report.py integration
- 2. Subprocess execution with asyncio (python generate_full_report.py {stockid})
- 3. `POST /api/data/structured/generate` endpoint with stockid parameter
- 4. Parse 14 sections from script output (separated by "=" * 80)
- 5. Filter sections based on `sections` parameter (user selection)
- 6. Reorder sections based on `section_order` parameter
- 7. Timeout: 60 seconds (configurable)
- 11. No caching - always generate fresh

**New Dev Notes Section**:
```markdown
### generate_full_report.py Integration

**Script Location**: `structured_report_builder/generate_full_report.py`

**Execution**:
```python
process = await asyncio.create_subprocess_exec(
    "python", "structured_report_builder/generate_full_report.py",
    str(stockid), str(exchange),
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
```

**Output Format**:
- 14 sections separated by 80 "=" characters
- Each section has title (first line) + content

**Sections**:
1. Company Information
2. Income Statement (Quarterly)
3. Income Statement (Annual)
4. Balance Sheet
5. Cash Flow
6. Ratios
7. Valuation
8. Shareholding
9. Stock Performance
10. Technical Analysis
11. Quality Assessment
12. Financial Trend
13. Proprietary Score
14. Peer Comparison

**Parsing Logic**:
```python
sections = raw_output.split("=" * 80)
for idx, section_text in enumerate(sections, start=1):
    lines = section_text.strip().split("\n")
    title = lines[0].strip()
    content = "\n".join(lines[1:])
    parsed_sections[str(idx)] = {"title": title, "content": content}
```
```

---

### Story 2.5: Structured Data Display and Section Preview
**Status**: Draft → **Update Required**

**Major Changes**:

1. **Display 14 sections as checkboxes** (AC: 1, 2 - modified)
   - **OLD**: Display sections from parser automatically
   - **NEW**: Display 14 sections as checkboxes (only if data_mode is NEW or OLD_NEW)
   - User selects which sections to include
   - Default: all sections selected

2. **Add drag-drop reordering** (AC: new)
   - Use React DnD for section reordering
   - Visual feedback during drag (highlighting drop zones)
   - Save section_order to data_config

3. **Conditional display based on data mode** (AC: new)
   - If OLD mode: Hide section selection, show OLD data preview only
   - If NEW or OLD_NEW mode: Show 14 section checkboxes + drag-drop

4. **Preview merged data** (AC: 9 - modified)
   - If OLD_NEW mode: "Preview Merged Data" button
   - Calls `POST /api/data/merge` endpoint (Story 1.7 - new backend service)
   - Shows OLD data + selected NEW sections combined

**Updated Acceptance Criteria**:
- 1. 14 section checkboxes displayed (only if data_mode is NEW or OLD_NEW)
- 2. Section titles from generate_full_report.py: Company Info, Income Statement (Q), Income Statement (A), etc.
- 3. Drag-drop reordering with React DnD
- 4. Selected sections highlighted with checkmarks
- 9. "Preview Merged Data" button (if OLD_NEW mode) shows combined result
- 11. Conditional UI: section selection hidden if data_mode is OLD

---

## Epic 3: Prompt Engineering Updates

### Story 3.2: Tabbed Prompt Editor with Syntax Highlighting
**Status**: Draft → **Update Required**

**Major Changes**:

1. **Add multi-type prompt support** (AC: new)
   - **OLD**: Single prompt editor
   - **NEW**: Three independent prompts (paid/unpaid/crawler)
   - Paid is required, unpaid and crawler are optional

2. **Implement tabbed interface** (AC: 1, 2 - modified)
   - Horizontal tabs: [💰 Paid] [🆓 Unpaid] [🕷️ Crawler]
   - Active tab highlighted with blue underline
   - Clicking tab switches editor content
   - Each prompt type maintains its own template

3. **Add prompt type selection** (AC: new)
   - Checkboxes above tabs: Paid ☑, Unpaid ☐, Crawler ☐
   - Paid always visible and checked (required)
   - Unchecked types hidden from tabs
   - Only checked types will be used for generation

4. **Pre-populate with existing prompts** (AC: new)
   - Fetch existing prompts: `GET /api/triggers/{trigger_name}/prompts`
   - Auto-fill Monaco editors with existing prompt templates
   - If no existing prompt: Start with blank or example template

5. **Shared data across prompt types** (AC: new)
   - All prompt types use same data configuration (from Story 2.5)
   - Same sections available for placeholders in all types
   - Autocomplete suggestions shared across tabs

**Updated Acceptance Criteria**:
- 1. Monaco Editor with tabbed interface for 3 prompt types
- 2. Tabs: [💰 Paid] [🆓 Unpaid] [🕷️ Crawler]
- 3. Checkboxes to enable/disable unpaid and crawler types
- 4. Paid prompt is always visible and required
- 5. Pre-populate editors with existing prompts from trigger_prompts collection
- 6. Tab switching preserves each prompt's content (auto-save to context)
- 14. Shared autocomplete suggestions (data is common across all types)

**New Dev Notes Section**:
```markdown
### Multi-Type Prompt Architecture

**Prompt Types**:
- **Paid**: Primary audience (paid subscribers), detailed analysis
- **Unpaid**: Free users, brief summary
- **Crawler**: SEO/web crawler content, keyword-optimized

**Storage**:
```javascript
{
  "prompts": {
    "paid": "Generate detailed article for {{company_name}}...",
    "unpaid": "Generate brief summary for {{company_name}}...",
    "crawler": null  // Optional
  }
}
```

**Frontend State**:
```typescript
interface PromptEditorState {
  enabledTypes: ("paid" | "unpaid" | "crawler")[];
  activeTab: "paid" | "unpaid" | "crawler";
  draftPrompts: {
    paid: string;
    unpaid: string;
    crawler: string;
  };
}
```

**Tab Visibility**:
- Paid tab: always visible
- Unpaid tab: visible if checkbox checked
- Crawler tab: visible if checkbox checked
```

---

### Story 3.3: Data Placeholder Validation
**Status**: Draft → **Update Required**

**Changes Needed**:

1. **Validate per active tab** (AC: 1, 2 - modified)
   - Run validation only for currently active tab's prompt
   - Show tab indicator (warning icon) if errors exist in that tab
   - Validation summary shows errors for active tab only

2. **Shared autocomplete** (AC: 4 - modified)
   - Same sections available for all prompt types (data is shared)
   - Autocomplete shows sections based on data_mode and selected sections
   - If OLD mode: show OLD data fields
   - If NEW or OLD_NEW mode: show section placeholders ({{section_1}}, {{section_2}}, etc.)

**Updated Acceptance Criteria**:
- 3. Tab indicator shows validation status (warning icon if errors in that tab's prompt)
- 4. Autocomplete suggestions shared across all tabs (data configuration is common)
- 11. Validation runs per tab when tab becomes active

---

### Story 3.4: Prompt Preview with Data Substitution
**Status**: Draft → **Update Required**

**Changes Needed**:

1. **Preview per prompt type** (AC: 1, 2 - modified)
   - "Preview Prompt" button triggers substitution for currently active tab
   - Preview shows final prompt for selected prompt type only
   - Modal can show tabs to preview all checked prompt types if desired

2. **Data substitution based on data mode** (AC: 3 - modified)
   - If OLD mode: Replace placeholders with OLD data from news_triggers
   - If NEW mode: Replace placeholders with generated sections
   - If OLD_NEW mode: Replace with merged data (OLD + NEW sections)

3. **Metadata includes prompt type** (AC: 10 - modified)
   - Preview metadata shows: stock ID, trigger name, **prompt type** (paid/unpaid/crawler), timestamp

**Updated Acceptance Criteria**:
- 10. Preview metadata includes prompt_type field
- 11. Preview modal can show tabs for all checked prompt types

---

## Epic 4: Multi-Model Generation Updates

### Story 4.1: LLM Abstraction Layer and Provider Integration
**Status**: Draft → **Update Required**

**Changes Needed**:

1. **Remove Google provider** (AC: 2, 3 - modified)
   - **OLD**: OpenAI, Anthropic, Google
   - **NEW**: OpenAI, Anthropic only (per user requirement: "remove Google")

2. **Add adaptive routing logic** (AC: new)
   - Check `trigger_prompts.isActive` flag before generation
   - If isActive=false or not found: Use legacy 3-prompt method
   - If isActive=true: Use new single HTML prompt method

3. **Add HTML extraction** (AC: new)
   - New method: `_extract_components(html_content: str) -> Dict`
   - Extract `<title>`, `<meta name="description">`, `<article>` from HTML
   - Return: `{"title": "...", "summary": "...", "article": "..."}`

**Updated Acceptance Criteria**:
- 2. Concrete implementations for OpenAI (GPT-4o) and Anthropic (Claude Sonnet 4.5) only
- 11. Add NewsGenerationService.generate_news() method with isActive flag check
- 12. Add HTML extraction logic for new method
- 13. Legacy generation method for backward compatibility

**New Dev Notes Section**:
```markdown
### Adaptive Generation Routing

**isActive Flag Logic**:
```python
config = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

if not config or not config.get("isActive"):
    # Legacy 3-prompt method
    return await self._legacy_generation(stockid, prompt_type)
else:
    # New single HTML prompt method
    merged_data = await data_merge_service.merge_data(...)
    html_output = await generator.generate(merged_data, config["prompts"][prompt_type], ...)
    return self._extract_components(html_output)
```

**Legacy Method**:
- Calls existing `generate_news_og.py` script
- Three separate prompts: headline, summary, article
- Returns same format as new method

**New Method**:
- Single comprehensive prompt generating full HTML
- Extracts title/summary/article from HTML using regex
- Supports both OpenAI and Claude
```

---

### Story 4.3: Parallel News Generation
**Status**: Draft → **Update Required**

**Major Changes**:

1. **Update endpoint** (AC: 1 - modified)
   - **OLD**: `POST /api/triggers/:id/generate` with selected models
   - **NEW**: `POST /api/news/generate` with trigger_name, stockid, prompt_type
   - Single generation per call (not parallel across models for MVP)
   - Frontend calls endpoint once per checked prompt type

2. **Add adaptive routing** (AC: new)
   - Service checks isActive flag
   - Routes to legacy or new generation method
   - Returns consistent format regardless of method

3. **Generate per prompt type** (AC: 2, 3 - modified)
   - **OLD**: Generate across multiple models in parallel
   - **NEW**: Generate for specific prompt_type (paid/unpaid/crawler)
   - Frontend loops through checked prompt types
   - Example: If paid and unpaid checked → 2 API calls

4. **Status tracking per prompt type** (AC: 4 - modified)
   - Status indicators: Pending, Generating, Complete, Failed
   - Grouped by prompt type (💰 Paid: Complete, 🆓 Unpaid: Generating)

5. **Save to generation_history** (AC: 10 - modified)
   - Store each generation with prompt_type field
   - Include method ("new" | "legacy"), tokens, cost, generation_time
   - Status: "success" | "failed"

**Updated Acceptance Criteria**:
- 1. `POST /api/news/generate` endpoint with trigger_name, stockid, prompt_type
- 2. Check isActive flag and route to appropriate generation method
- 3. Generate news for specific prompt_type (paid/unpaid/crawler)
- 4. Status updates per prompt type (not per model for MVP)
- 10. Save to generation_history collection with method and prompt_type fields

**Simplified for MVP** (defer to Phase 2):
- Multi-model parallel testing (test single model first)
- Side-by-side model comparison (focus on single model + prompt type variation)

---

### Story 4.4: Grouped Result Comparison
**Status**: Draft → **Update Required**

**Major Changes**:

1. **Group by prompt type instead of model** (AC: 1, 2 - modified)
   - **OLD**: Group by model (GPT-4 | Claude | Gemini)
   - **NEW**: Group by prompt type (💰 Paid | 🆓 Unpaid | 🕷️ Crawler)
   - Within each group: show single result (not multiple models for MVP)

2. **Colored headers per prompt type** (AC: 2 - modified)
   - 💰 Paid: Blue header (#0d6efd)
   - 🆓 Unpaid: Green header (#198754)
   - 🕷️ Crawler: Orange header (#fd7e14)

3. **Metadata includes generation method** (AC: 5, 22 - modified)
   - Show: Tokens | Time | Cost | **Method** (New/Legacy)
   - If legacy method: Show note "Generated using legacy 3-prompt method"

**Updated Acceptance Criteria**:
- 1. Results grouped by prompt type (not model)
- 2. Colored headers: Paid (blue), Unpaid (green), Crawler (orange)
- 5. Metadata includes method field ("new" | "legacy")
- 22. Show generation metadata per prompt type

---

## Epic 5: Publishing Updates

### Story 5.2: Configuration Publishing with Confirmation
**Status**: Draft → **Update Required**

**Major Changes**:

1. **Set isActive=true on publish** (AC: 6 - modified)
   - **OLD**: Save configuration to database
   - **NEW**: Save configuration AND set isActive=true
   - This activates new generation method for this trigger

2. **Publish all prompt types** (AC: 2 - modified)
   - Confirmation modal shows all three prompt types (paid/unpaid/crawler)
   - Expandable sections per type to view full prompt
   - All checked types published together (atomic update)

3. **Increment version** (AC: 6 - modified)
   - Auto-increment version field on each publish
   - Save snapshot to prompt_versions collection

4. **Validation before publish** (AC: 1 - modified)
   - Check: paid prompt exists and tested
   - Check: data_config defined (data_mode, sections if NEW/OLD_NEW)
   - Check: model_config defined (provider, model, temperature)
   - Check: At least one successful preview generation exists

**Updated Acceptance Criteria**:
- 6. Backend sets isActive=true on publish (enables new generation method)
- 7. Only one active config per trigger (deactivate previous when publishing new)
- 9. Success notification shows version number and "isActive=true" status
- 11. Save snapshot to prompt_versions collection for rollback capability

---

### Story 5.5: Production Integration and Active Configuration API
**Status**: Draft → **Update Required**

**Changes Needed**:

1. **Update active config API response** (AC: 2 - modified)
   - Include all new fields: isActive, model_config, data_config, prompts (all 3 types)
   - Document: "Check isActive field before using new fields"

2. **Add backward compatibility note** (AC: 9 - new)
   - If isActive=false or missing: Use legacy generation (existing generate_news_og.py)
   - If isActive=true: Use new generation method with data_config and prompts

3. **Update integration documentation** (AC: 7 - modified)
   - Document isActive flag usage
   - Provide code examples for both legacy and new method routing

**Updated Acceptance Criteria**:
- 2. Response includes isActive, model_config, data_config, prompts fields
- 9. Backward compatibility: triggers without isActive use legacy method
- 10. Integration documentation updated with adaptive routing examples

---

## New Stories Required (Not Updates)

The following stories are entirely new and don't update existing ones:

### Story 1.4: Database Schema Updates (NEW - Keep as created)
- Pydantic models for News CMS Workflow
- Extend trigger_prompts collection
- Create generation_history and prompt_versions collections
- Create indexes

### Story 1.5: Trigger Data APIs (NEW - Rename from 1.5.aws-deployment)
- `GET /api/triggers/{trigger_name}/data?stockid={stockid}`
- `GET /api/triggers/{trigger_name}/prompts`
- stockid validation, no caching

### Story 1.7: Data Merge Service (NEW)
- `POST /api/data/merge` endpoint
- Merge OLD + NEW data based on data_mode
- Used by preview and publish flows

### Story 1.8: Configuration Save & Publish APIs (NEW)
- `POST /api/config/save` (draft, isActive=false)
- `POST /api/config/publish` (set isActive=true, increment version)
- `GET /api/config/{trigger_name}`

### Story 1.9: News Generation Service Integration (NEW)
- Consolidate adaptive routing logic
- NewsGenerationService with isActive check
- HTML extraction for new method
- Legacy method fallback

---

## Story Renumbering Proposal

To accommodate new stories, propose renumbering:

**Epic 1 (Foundation)**:
- 1.1: Project Setup (existing, Done)
- 1.2: MongoDB Setup (existing, Done) → **UPDATE**
- 1.3: Basic UI Shell (existing, Done)
- 1.4: Database Schema Updates (NEW, Keep)
- 1.5: Trigger Data APIs (NEW)
- 1.6: Trigger Management Dashboard (RENAME from 1.4)
- 1.7: AWS Deployment (RENAME from 1.5)
- 1.8: Data Merge Service (NEW)
- 1.9: Configuration APIs (NEW)
- 1.10: News Generation Service (NEW)

**Epic 2 (Data Pipeline)**: Update 2.3, 2.4, 2.5

**Epic 3 (Prompts)**: Update 3.2, 3.3, 3.4

**Epic 4 (Generation)**: Update 4.1, 4.3, 4.4

**Epic 5 (Publishing)**: Update 5.2, 5.5

---

## Implementation Priority

### Phase 1: Foundation (Weeks 1-2)
1. Story 1.4: Database Schema Updates
2. Story 1.5: Trigger Data APIs
3. Update Story 1.2: MongoDB with new collections
4. Story 1.8: Configuration APIs
5. Story 1.9: Data Merge Service

### Phase 2: Data Pipeline (Weeks 3-4)
6. Update Story 2.3: Data Retrieval with stockid + data modes
7. Update Story 2.4: Parser Integration with generate_full_report.py
8. Update Story 2.5: Structured Data Display with checkboxes

### Phase 3: Prompt Engineering (Weeks 5-6)
9. Update Story 3.2: Tabbed Prompt Editor with multi-type prompts
10. Update Story 3.3: Validation per tab
11. Update Story 3.4: Preview per prompt type

### Phase 4: Generation & Publishing (Weeks 7-8)
12. Update Story 4.1: LLM Abstraction with adaptive routing
13. Update Story 4.3: Generation per prompt type
14. Update Story 4.4: Results grouped by prompt type
15. Update Story 5.2: Publishing with isActive=true
16. Update Story 5.5: Production integration documentation

---

## Next Steps

1. **Review this document** with team for approval
2. **Create backup** of existing story files before updating
3. **Update stories incrementally** by epic (not all at once)
4. **Test backward compatibility** after each update
5. **Document breaking changes** in story Change Logs

---

**Document Version**: 1.0
**Last Updated**: 2025-10-30
**Author**: Dev Agent (Claude Code)
