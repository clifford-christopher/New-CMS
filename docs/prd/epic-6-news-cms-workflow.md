# Epic 6: News CMS Workflow Feature

**Status**: ✅ **Implemented** (Updated November 2025 for v2.3 workflow)

**Goal**: Build a comprehensive workflow that enables content managers to configure news generation using structured data from Python report generators, manage multi-type prompts (paid/unpaid/crawler), test across multiple LLM models, and publish configurations with backward compatibility to existing news generation systems.

**v2.3 Update**: Story 1.11 now implements two-phase workflow - Phase 1 (Data Configuration with section selection), Phase 2 (Section Management with drag-and-drop ordering).

## Background Context

The News CMS Workflow Feature addresses the need to integrate structured financial data generation with AI-powered news creation. This epic builds upon the existing Foundation (Epic 1) to add:

1. **Data Configuration**: Integration with 14-section structured report builder (`generate_full_report.py`)
2. **Data Mode Selection**: Support for OLD (existing trigger data), NEW (generated reports), and OLD_NEW (merged) data sources
3. **Multi-Type Prompts**: Independent prompt templates for paid, unpaid, and crawler content distribution channels
4. **Adaptive Generation**: Backward-compatible news generation that checks `isActive` flag to route between legacy (3-prompt) and new (single HTML prompt) methods
5. **Pre-population UX**: Always show existing data and prompts first for reference before configuration

## Key Requirements Addressed

### Data Model Clarification
- **OLD data** = `news_triggers.data` (existing stockid-specific input from database) - **Treated as single "Old Data" section** with `id='old'`, not split into 14 sections
- **NEW data** = 14 sections from `generate_full_report.py {stockid}` (freshly generated structured report) - Sections 1-14 with `source='new'`
- **OLD_NEW data** = Merge of single "Old Data" section + selected sections from NEW report

### Critical Technical Decisions
1. **stockid-Specific APIs**: All data fetching requires both `trigger_name` AND `stockid` parameters
2. **No Caching for Structured Data**: Data is time-sensitive (changes during market hours 9:15 AM - 3:30 PM IST), always generate fresh
3. **Cache Only Static Configs**: Prompt templates, model configurations, user metadata (not trigger data or generation history)
4. **Backward Compatibility**: `isActive=false` uses legacy 3-prompt method, `isActive=true` uses new single HTML prompt method

### User Experience Flow
1. **Reference First**: Display existing OLD data + existing prompts before any configuration
2. **Data Mode Choice**: User explicitly selects OLD | NEW | OLD_NEW with radio buttons
3. **Conditional UI**: Section selection (14 checkboxes + drag-drop) only shown if NEW or OLD_NEW selected
4. **Pre-population**: Existing prompts from `trigger_prompts` auto-fill Monaco editors
5. **Shared Configuration**: Data config, section management, model selection shared across all prompt types
6. **Independent Prompts**: Separate prompt templates per type (paid/unpaid/crawler) via tabbed interface

## Story List

### Story 1.4: Database Schema Updates for News CMS Workflow

**As a** developer,
**I want** MongoDB collections extended to support workflow configuration data,
**so that** the system can persist trigger configurations with data modes, section selections, and multi-type prompts.

**Acceptance Criteria**:
1. Extend `trigger_prompts` collection schema with new fields:
   - `isActive` (boolean, default: false)
   - `model_config` (object: provider, model, temperature)
   - `data_config` (object: data_mode ["old"|"new"|"old_new"], sections [array], section_order [array])
   - `prompts` (object: paid, unpaid, crawler - each with template string)
   - `version` (integer, auto-increment)
   - `updated_at` (datetime)
2. Pydantic models created for:
   - `TriggerPromptConfig` (full configuration)
   - `DataConfig` (data_mode, sections, section_order)
   - `ModelConfig` (provider, model, temperature, max_tokens)
   - `PromptTemplates` (paid, unpaid, crawler)
3. Create `generation_history` collection schema:
   - `trigger_name`, `stockid`, `data_mode`, `prompt_type`, `model`, `timestamp`
   - `input_data`, `generated_html`, `extracted_title`, `extracted_summary`, `extracted_article`
   - `tokens_used`, `cost`, `generation_time`
4. Create `prompt_versions` collection for rollback capability:
   - `trigger_name`, `version`, `prompts`, `model_config`, `data_config`, `published_at`, `published_by`
5. Migration script or documentation creates indexes:
   - `trigger_prompts`: trigger_name (unique), isActive
   - `generation_history`: trigger_name + stockid + timestamp, prompt_type
   - `prompt_versions`: trigger_name + version
6. Validation rules enforced at Pydantic level:
   - data_mode must be one of ["old", "new", "old_new"]
   - sections must be array of integers 1-14, no duplicates
   - section_order must match length of sections
   - prompts.paid is required, prompts.unpaid and prompts.crawler optional
7. Meets NFR11: Backward compatibility - existing trigger_prompts documents without new fields still work

### Story 1.5: Trigger Data API with stockid Parameter

**As a** content manager,
**I want** to fetch existing trigger input data for a specific stockid,
**so that** I can see the OLD data that will be used if I select "OLD only" mode.

**Acceptance Criteria**:
1. FastAPI endpoint `GET /api/triggers/{trigger_name}/data?stockid={stockid}` created
2. Query MongoDB: `news_triggers.find_one({"trigger_name": [trigger_name], "stockid": stockid})`
3. Response format:
   ```json
   {
     "trigger_name": "earnings_result",
     "stockid": 513374,
     "data": { /* existing input data from news_triggers */ },
     "metadata": {
       "last_updated": "2025-10-28T10:30:00Z",
       "data_source": "news_triggers"
     }
   }
   ```
4. stockid parameter validation: must be positive integer, required
5. Error handling:
   - 404 if trigger_name or stockid not found with message: "No data found for trigger '{trigger_name}' with stockid {stockid}"
   - 400 if stockid invalid format
6. No caching (data may change during market hours)
7. Response time meets NFR2: completes within 5 seconds
8. Endpoint logged with trigger_name, stockid, response time for monitoring
9. FastAPI endpoint `GET /api/triggers/{trigger_name}/prompts` created to fetch existing prompts:
   ```json
   {
     "trigger_name": "earnings_result",
     "prompts": {
       "paid": "existing prompt template...",
       "unpaid": "existing unpaid prompt...",
       "crawler": "existing crawler prompt..."
     },
     "model_config": { /* if exists */ },
     "data_config": { /* if exists */ }
   }
   ```
10. Prompts endpoint returns empty prompts if none configured (not 404)

### Story 1.6: Structured Data Service with stockid Parameter

**As a** content manager,
**I want** to generate fresh structured data from 14-section report builder for a specific stockid,
**so that** I can select which sections to include when choosing "NEW" or "OLD+NEW" modes.

**Acceptance Criteria**:
1. FastAPI endpoint `POST /api/data/structured/generate` created with request body:
   ```json
   {
     "stockid": 513374,
     "sections": [1, 2, 3, 5, 7, 9, 12],  // optional, defaults to all 14
     "section_order": [1, 2, 3, 5, 7, 9, 12],  // optional, defaults to sequential
     "exchange": 0  // optional, defaults to 0
   }
   ```
2. Python service `StructuredDataService` created in `backend/app/services/structured_data_service.py`:
   - Method: `async def generate_report(stockid: int, sections: List[int], section_order: List[int], exchange: int) -> Dict`
   - Invokes `generate_full_report.py` via asyncio subprocess:
     ```python
     process = await asyncio.create_subprocess_exec(
         "python", str(script_path), str(stockid), str(exchange),
         stdout=asyncio.subprocess.PIPE,
         stderr=asyncio.subprocess.PIPE
     )
     ```
   - Parses output (14 sections separated by 80 "=" characters)
   - Filters sections based on `sections` parameter
   - Reorders sections based on `section_order` parameter
3. Response format:
   ```json
   {
     "stockid": 513374,
     "sections": {
       "1": { "title": "Company Information", "content": "..." },
       "2": { "title": "Income Statement (Quarterly)", "content": "..." },
       ...
     },
     "section_order": [1, 2, 3, 5, 7, 9, 12],
     "metadata": {
       "generated_at": "2025-10-30T14:30:00Z",
       "script_execution_time": 8.3,
       "data_source": "generate_full_report.py"
     }
   }
   ```
4. Async job pattern: Long-running generations return `job_id` for polling:
   ```json
   {
     "job_id": "uuid-1234",
     "status": "processing",
     "message": "Generating structured data for stockid 513374"
   }
   ```
5. FastAPI endpoint `GET /api/data/structured/status/{job_id}` for polling job status
6. Error handling:
   - Subprocess timeout (default 60 seconds configurable)
   - Script execution failure (non-zero exit code) with stderr captured
   - Invalid stockid (script returns error)
7. No caching (always generate fresh data)
8. Validation:
   - sections must be subset of [1..14]
   - section_order must match sections length and contain same values
9. Logging: stockid, execution time, success/failure, errors
10. Meets NFR3: generation completes within 60 seconds (configurable timeout)

### Story 1.7: Data Merge Service for OLD_NEW Mode

**As a** content manager,
**I want** the system to merge OLD trigger data with NEW structured sections when I select "OLD+NEW" mode,
**so that** I can combine existing input data with freshly generated report sections.

**Acceptance Criteria**:
1. Python service `DataMergeService` created in `backend/app/services/data_merge_service.py`
2. Method: `async def merge_data(trigger_name: str, stockid: int, data_mode: str, sections: List[int], section_order: List[int]) -> Dict`
3. Logic by data_mode:
   - **"old"**: Fetch and return `news_triggers.data` as-is (no section generation)
   - **"new"**: Generate structured data, return selected sections only
   - **"old_new"**:
     - Fetch OLD data from `news_triggers.find_one({trigger_name, stockid}).data`
     - Generate NEW data via `StructuredDataService`
     - Concatenate: `{...old_data, "structured_sections": {...new_sections}}`
4. Response format:
   ```json
   {
     "data_mode": "old_new",
     "stockid": 513374,
     "merged_data": {
       /* old data fields from news_triggers */
       "trigger_data": { ... },
       /* new structured sections */
       "structured_sections": {
         "1": { "title": "Company Information", "content": "..." },
         "2": { "title": "Income Statement", "content": "..." }
       }
     },
     "metadata": {
       "old_data_source": "news_triggers",
       "new_data_source": "generate_full_report.py",
       "merged_at": "2025-10-30T14:35:00Z"
     }
   }
   ```
5. FastAPI endpoint `POST /api/data/merge` exposes this service:
   ```json
   {
     "trigger_name": "earnings_result",
     "stockid": 513374,
     "data_mode": "old_new",
     "sections": [1, 2, 3],
     "section_order": [1, 2, 3]
   }
   ```
6. Error handling:
   - OLD data not found: Warning logged but continue with NEW only
   - NEW data generation failure: Return error, don't proceed
7. Validation: data_mode must be one of ["old", "new", "old_new"]
8. Used by preview and publish flows to prepare final data for LLM
9. No caching (data is dynamic)
10. Unit tests cover all three data modes with mock data

### Story 1.8: Configuration Save and Publish APIs

**As a** content manager,
**I want** to save my configuration as a draft and publish it when ready,
**so that** I can iteratively build my configuration without affecting production.

**Acceptance Criteria**:
1. FastAPI endpoint `POST /api/config/save` saves draft configuration:
   ```json
   {
     "trigger_name": "earnings_result",
     "data_config": {
       "data_mode": "old_new",
       "sections": [1, 2, 3, 5],
       "section_order": [1, 2, 3, 5]
     },
     "model_config": {
       "provider": "claude",
       "model": "claude-sonnet-4-5-20250929",
       "temperature": 0.7,
       "max_tokens": 20000
     },
     "prompts": {
       "paid": "Generate a detailed article...",
       "unpaid": "Generate a brief summary...",
       "crawler": "Generate SEO-optimized content..."
     }
   }
   ```
2. Backend updates or creates document in `trigger_prompts` collection with `isActive: false`
3. Response: `{ "status": "saved", "version": 1, "is_active": false }`
4. FastAPI endpoint `POST /api/config/publish` publishes configuration:
   - Validates all required fields present
   - Validates at least one successful test generation exists (check `generation_history`)
   - Sets `isActive: true`
   - Increments version number
   - Saves to `prompt_versions` collection for history
   - Logs to audit trail
5. Only one active configuration per trigger_name (deactivate previous when publishing new)
6. FastAPI endpoint `GET /api/config/{trigger_name}` retrieves current configuration (active or latest draft)
7. Response includes all fields: data_config, model_config, prompts, version, is_active, updated_at
8. Validation rules:
   - prompts.paid is required (paid is primary audience)
   - If data_mode is "new" or "old_new", sections must not be empty
   - section_order must match sections
   - model_config.provider must be one of ["openai", "claude"]
9. Meets FR25, FR27, FR28: publish function with validation, versioning, and activation
10. Atomic update: Use MongoDB transaction to ensure consistency

### Story 1.9: News Generation Service with Adaptive Routing

**As a** developer,
**I want** a news generation service that checks `isActive` flag and routes to legacy or new generation methods,
**so that** existing triggers continue working while new configurations use enhanced workflow.

**Acceptance Criteria**:
1. Python service `NewsGenerationService` created in `backend/app/services/news_generation_service.py`
2. Main method: `async def generate_news(trigger_name: str, stockid: int, prompt_type: str) -> Dict`
3. Logic flow:
   ```python
   config = await db.trigger_prompts.find_one({"trigger_name": trigger_name})

   if not config or not config.get("isActive"):
       # Legacy 3-prompt method (existing generate_news_og.py)
       return await self._legacy_generation(stockid, prompt_type)
   else:
       # New single-prompt HTML method
       merged_data = await data_merge_service.merge_data(
           trigger_name, stockid,
           config["data_config"]["data_mode"],
           config["data_config"]["sections"],
           config["data_config"]["section_order"]
       )
       generator = self._get_generator(config["model_config"]["provider"])
       html_output = await generator.generate(
           merged_data,
           config["prompts"][prompt_type],
           config["model_config"]
       )
       extracted = self._extract_components(html_output)  # title/summary/article
       return extracted
   ```
4. Strategy pattern for LLM providers:
   ```python
   class NewsGenerator(ABC):
       @abstractmethod
       async def generate(self, stock_data: str, prompt: str, model_config: Dict) -> str:
           pass

   class ClaudeNewsGenerator(NewsGenerator):
       async def generate(self, stock_data: str, prompt: str, model_config: Dict) -> str:
           # Use Anthropic client, Claude Sonnet 4.5
           # Stream HTML output
           # Return full HTML

   class OpenAINewsGenerator(NewsGenerator):
       async def generate(self, stock_data: str, prompt: str, model_config: Dict) -> str:
           # Use OpenAI client, GPT-4o
           # Generate HTML output
           # Return full HTML
   ```
5. HTML extraction method `_extract_components(html_content: str) -> Dict`:
   - Uses regex to extract `<title>`, `<meta name="description">`, article body
   - Returns: `{"title": "...", "summary": "...", "article": "..."}`
6. Legacy generation method `_legacy_generation()`:
   - Calls existing `generate_news_og.py` script (3 separate prompts: headline, summary, article)
   - Returns same format: `{"title": "...", "summary": "...", "article": "..."}`
7. Error handling:
   - LLM API failures: Retry with exponential backoff (3 attempts)
   - Extraction failures: Log error, return raw HTML with warning
   - Legacy script failures: Log error, raise exception
8. Tracking metadata returned:
   ```json
   {
     "title": "TCS Reports Strong Q4 Earnings",
     "summary": "...",
     "article": "...",
     "metadata": {
       "method": "new" | "legacy",
       "model": "claude-sonnet-4-5-20250929",
       "tokens_used": 3456,
       "generation_time": 12.5,
       "cost": 0.15,
       "prompt_type": "paid"
     }
   }
   ```
9. FastAPI endpoint `POST /api/news/generate` exposes this service:
   ```json
   {
     "trigger_name": "earnings_result",
     "stockid": 513374,
     "prompt_type": "paid"  // or "unpaid" or "crawler"
   }
   ```
10. Meets NFR11: Backward compatibility - triggers without isActive or with isActive=false use legacy method
11. Unit tests mock both legacy and new generation paths
12. Integration tests with real Claude/OpenAI APIs (rate-limited)

### Story 1.10: Trigger Selection Dashboard (Frontend)

**As a** content manager,
**I want** to select a trigger and enter a stockid to begin configuration,
**so that** I can start the workflow with the necessary context.

**Acceptance Criteria**:
1. Next.js page created: `app/workflow/page.tsx`
2. Page displays:
   - Dropdown or searchable list of trigger_names (fetched from `GET /api/triggers`)
   - Number input field for stockid
   - "Load Configuration" button
3. On button click:
   - Fetch OLD data: `GET /api/triggers/{trigger_name}/data?stockid={stockid}`
   - Fetch existing prompts: `GET /api/triggers/{trigger_name}/prompts`
   - Navigate to Data Configuration page with context stored in React Context
4. Reference panel displays:
   - **OLD Data Preview**: Bootstrap Card showing existing trigger data (collapsible JSON view)
   - **Existing Prompts**: 3 collapsible cards showing paid/unpaid/crawler prompts (if configured)
   - If no prompts exist: Show placeholder "No existing prompts - you'll create new ones"
5. React Context `WorkflowContext` created to store:
   - trigger_name, stockid
   - old_data (from news_triggers)
   - existing_prompts (from trigger_prompts)
   - Selected data_mode, sections, section_order
   - Draft prompts (paid/unpaid/crawler)
   - Model config
6. Loading states while fetching data
7. Error handling:
   - trigger_name not found: Show error message
   - stockid not found: Show warning "No existing data for this stockid, you can still create configuration"
8. Meets FR1, FR2: Display triggers and accept stockid input
9. Bootstrap 5 styling with responsive layout
10. Validation: stockid must be positive integer before allowing "Load Configuration"

### Story 1.11: Data Configuration and Section Management (Frontend)

**As a** content manager,
**I want** to select data mode (OLD/NEW/OLD_NEW), SELECT which sections to include (Data Configuration), and then REORDER those sections (Section Management),
**so that** I have full control over what data feeds into my prompts and in what order.

**Purpose**: This story covers the TWO-PHASE workflow:
- **Phase 1 (Data Configuration)**: Fetch/generate data + SELECT sections with checkboxes
- **Phase 2 (Section Management)**: REORDER selected sections using drag-and-drop

**Acceptance Criteria**:

**Phase 1: Data Configuration (Selection)**

1. Next.js page with tabbed interface: Data Configuration | Section Management | Prompts | Testing | Results
2. **Data Configuration Tab** - Data mode selection:
   - Radio buttons or dropdown for data mode:
     - ⚪ OLD only (use existing news_triggers.data as single "Old Data" section)
     - ⚪ NEW only (generate 14 sections, select which to use)
     - ⚪ OLD + NEW (combine single "Old Data" section with selected NEW sections)
   - Default pre-selected based on existing config if editing, else "OLD" default

3. **Data Fetch/Generation**:
   - **OLD Mode**: "Fetch Data" button → `GET /api/stocks/{stockid}/trigger-data?trigger_name={trigger}`
   - **NEW Mode**: "Generate Complete Report" button → `POST /api/data/structured/generate` (generates all 14 sections)
   - **OLD_NEW Mode**: Fetches OLD data + generates NEW data (both operations)
   - Loading spinner with status message (e.g., "Generating report... 8-15 seconds")
   - Cached data notification if data already exists for current stock ID

4. **Section Selection UI (NEW/OLD_NEW modes)**:
   - After generation, display all 14 sections with checkboxes using NewDataDisplay component
   - Each section shows: Checkbox | Section number badge | Section title | Expand/collapse
   - **View Toggle**: "All Sections" button | "Selected Only" button
   - **Bulk Actions**: "Select All" button | "Clear All" button
   - Selected count indicator: "5 sections selected"
   - Visual highlight: Selected sections have blue border and light blue background

5. **Section Preview**:
   - OLD Mode: OldDataDisplay component (read-only JSON view)
   - NEW/OLD_NEW Mode: NewDataDisplay component with collapsible section cards
   - Each section shows source badge: OLD (blue) or NEW (green)

6. **"Use This Data" Button**:
   - OLD Mode: Enabled after data fetch, labeled "Use This Data"
   - NEW Mode: Enabled when selections > 0, labeled "Use This Data (X sections)"
   - OLD_NEW Mode: Enabled when NEW selections > 0, labeled "Use This Data (OLD + X sections)"
   - Button click: Navigates to Section Management tab (activeStep = 'sections')

**Phase 2: Section Management (Ordering)**

7. **Section Management Tab** - Receives selected sections from Data Configuration:
   - **OLD Mode**: Shows single section `{id: 'old_data', name: 'OLD Data (Complete)', source: 'old'}`
     - Drag handle disabled (read-only)
     - Info: "No reordering needed. Proceed to configure prompts."

   - **NEW Mode**: Shows only selected NEW sections (e.g., sections 1, 3, 5, 9)
     - Each section: Drag handle | Section number badge | Section name | Source badge (green "NEW")
     - Drag-and-drop reordering enabled
     - Section count: "Section Order (4 sections)"

   - **OLD_NEW Mode**: Shows OLD section + selected NEW sections in combined draggable list
     - Initial order: OLD section first, then NEW sections
     - Example display:
       ```
       [1] 🔵 OLD Data (Complete) [drag handle]
       [2] 🟢 Section 1: Company Information [drag handle]
       [3] 🟢 Section 5: Cash Flow [drag handle]
       ```
     - ALL sections draggable - user can position OLD anywhere relative to NEW sections
     - Section count: "Section Order (1 OLD + 2 NEW sections)"

8. **Drag-and-Drop Implementation**:
   - Uses React Beautiful DnD or React DnD library
   - Visual feedback: Semi-transparent item during drag, placeholder shows drop target
   - Hover state on drag handles
   - Keyboard accessibility (Arrow keys + Space)
   - "Reset Order" button resets to default order

9. **Data Persistence**:
   - React state management tracks:
     - `dataMode`: "old" | "new" | "old_new"
     - `selectedSectionIds`: Array of selected section IDs (e.g., ["1", "3", "5"])
     - `sectionOrder`: Array tracking final order of sections
   - localStorage keys:
     - `fetchedOldData_{triggerId}`: Cached OLD data
     - `generatedNewData_{triggerId}`: Cached NEW sections (all 14)
     - `selectedSectionIds_{triggerId}`: User selections
     - `sectionOrder_{triggerId}`: Final order
   - Cache cleared on trigger change or explicit action

10. **Navigation Flow**:
    - Data Configuration → "Use This Data" button → Section Management tab
    - Section Management → "Continue to Prompts" button → Prompts tab
    - WorkflowContext updated with data_config and section_order

11. Meets FR4, FR5, FR6, FR9, FR11, FR12: Data source configuration with section selection and reordering
12. Error handling:
    - Generation timeout: Show error, allow retry
    - API failure: Show actionable error message
    - No sections selected: Disable "Use This Data" button with tooltip
13. Validation: NEW/OLD_NEW modes require at least 1 section selected to proceed

### Story 1.12: Prompt Configuration Page (Frontend)

**As a** content manager,
**I want** to create or edit prompts for paid, unpaid, and crawler types using pre-populated templates,
**so that** I can customize news generation for different audiences.

**Acceptance Criteria**:
1. Next.js page created: `app/workflow/[trigger_name]/prompt-config/page.tsx`
2. Page layout:
   - **Top**: Checkbox selection for prompt types (Paid ☑, Unpaid ☐, Crawler ☐)
     - Paid always visible and checked by default
     - Unpaid and Crawler optional
   - **Tabbed Interface**: Horizontal tabs showing only checked types
     - [💰 Paid] [🆓 Unpaid] [🕷️ Crawler]
     - Active tab highlighted with blue underline
     - Inactive tabs shown in gray
3. **Monaco Editor Integration**:
   - Monaco Editor component for active tab's prompt
   - Pre-populated with existing prompt from WorkflowContext (if exists)
   - If no existing prompt: Start with blank template or example prompt
   - Syntax highlighting for placeholders (e.g., `{{section_1}}`, `{data.field}`)
   - Line numbers, search/replace, keyboard shortcuts
   - Word count displayed per prompt
4. **Data Placeholder Autocomplete**:
   - When typing `{{`, show dropdown of available sections (based on selected sections from Data Config)
   - Autocomplete suggestions show section titles
   - Same suggestions for all tabs (since data is shared)
5. **Validation**:
   - Real-time validation of placeholders for active tab
   - Invalid placeholders underlined in red with hover tooltip
   - Validation error summary panel below editor
   - Tab indicator shows warning icon if errors in that tab's prompt
6. Tab switching:
   - Clicking tab switches editor content to that prompt type's template
   - Auto-save current prompt to WorkflowContext before switching
   - Debounced auto-save every 5 seconds
7. "Preview Prompt" button:
   - Substitutes placeholders with actual data (from Data Config step)
   - Opens modal showing final prompt for active tab
   - Shows estimated token count
   - "Copy to Clipboard" button
8. Save button: Updates WorkflowContext with prompts, navigates to Model Configuration
9. Meets FR13, FR14, FR15, FR16, FR35, FR36, FR37, FR38: Tabbed prompt editor with pre-population
10. Monaco Editor theme configurable (light/dark)

### Story 1.13: Model Configuration Page (Frontend)

**As a** content manager,
**I want** to select LLM model and configure settings that apply to all prompt types,
**so that** I can test generation with my preferred model.

**Acceptance Criteria**:
1. Next.js page created: `app/workflow/[trigger_name]/model-config/page.tsx`
2. Page layout:
   - **Provider Selection**: Radio buttons
     - ⚪ OpenAI (GPT-4o)
     - ⚪ Claude (Sonnet 4.5)
   - Note: Google removed as per user requirements
3. **Model Settings** (shown after provider selected):
   - Temperature slider: 0.0 to 1.0 (default 0.7)
   - Max Tokens input: number field (default 20000)
   - Help tooltips explaining each parameter
4. **Cost Estimation**:
   - Calculate estimated cost based on:
     - Average prompt size (from Data Config + Prompt Config)
     - Max tokens setting
     - Selected models
     - Number of checked prompt types
   - Display: "Estimated cost per generation: $0.08 (per prompt type)"
   - Display: "Total for 3 types: $0.24"
5. Pre-populate with existing model_config from WorkflowContext if editing
6. React state management:
   - provider state ("openai" | "claude")
   - model state (auto-selected based on provider)
   - temperature state
   - max_tokens state
7. Save button: Updates WorkflowContext with model_config, navigates to Preview & Publish
8. Meets FR17, FR18: Model selection with settings and cost estimates
9. Visual indicator: "Will generate for: 💰 Paid, 🆓 Unpaid" (based on checked types from Prompt Config)
10. Validation: Model must be selected before proceeding

### Story 1.14: Preview & Publish Page (Frontend)

**As a** content manager,
**I want** to generate preview news and publish my configuration when satisfied,
**so that** I can test before going live and deploy with confidence.

**Acceptance Criteria**:
1. Next.js page created: `app/workflow/[trigger_name]/preview-publish/page.tsx`
2. **Configuration Summary** (top section):
   - Data Mode: OLD / NEW / OLD_NEW
   - Sections: (list if NEW/OLD_NEW)
   - Model: Claude Sonnet 4.5 / OpenAI GPT-4o
   - Prompt Types: 💰 Paid, 🆓 Unpaid, 🕷️ Crawler (checkmarks)
   - Edit buttons for each section to go back
3. **Preview Generation Section**:
   - "Generate Preview" button (large, primary Bootstrap button)
   - Calls `POST /api/news/generate` for each checked prompt type
   - Loading spinner with status: "Generating Paid... ✓ Done | Generating Unpaid... ⏳"
   - Progress indicator: "2 of 3 complete"
4. **Results Display** (grouped by prompt type → model):
   - Section per prompt type with colored header:
     - 💰 Paid (blue header)
     - 🆓 Unpaid (green header)
     - 🕷️ Crawler (orange header)
   - Within each section:
     - **Title**: Extracted title from HTML
     - **Summary**: Extracted summary
     - **Article**: Full article content (collapsible for long content)
     - **Metadata**: 🎯 Tokens: 3456 | ⏱️ Time: 12.5s | 💰 Cost: $0.15
   - Collapsible sections to reduce scrolling
5. **Generation History** (sidebar or bottom panel):
   - List of previous preview generations in this session
   - Click to view historical results
   - Shows timestamp, prompt type, model
6. **Publish Flow**:
   - "Publish Configuration" button (only enabled after successful preview)
   - Opens confirmation modal:
     - Summary of what will be published (data config, model config, all 3 prompts)
     - Diff view if updating existing config
     - Warning: "This will activate configuration for production use"
   - "Confirm Publish" button in modal
   - Calls `POST /api/config/publish`
   - Success notification: "Published configuration v2 for earnings_result"
   - Redirect to dashboard or show "View Published Config" link
7. Meets FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR39, FR40
8. Error handling:
   - Preview generation failure: Show error for specific prompt type, allow retry
   - Publish validation failure: Show checklist of issues, prevent publish
9. Real-time status updates via polling (every 2 seconds) or SSE
10. Responsive design: Results stack on tablet (768-1199px)

### Story 1.15: Adaptive News Generation Script Integration

**As a** developer,
**I want** to ensure existing news generation scripts check the `isActive` flag,
**so that** automated news generation uses new configurations when available.

**Acceptance Criteria**:
1. Update existing `generate_news_og.py` or create new `generate_news_v2.py` wrapper
2. At start of generation flow, check MongoDB:
   ```python
   config = await db.trigger_prompts.find_one({
       "trigger_name": trigger_name,
       "isActive": True
   })
   ```
3. If config found and `isActive == True`:
   - Use new method: Call `NewsGenerationService.generate_news(trigger_name, stockid, prompt_type)`
   - Fetch merged data based on config.data_config
   - Use single HTML prompt from config.prompts[prompt_type]
   - Extract title/summary/article from HTML output
4. If config not found or `isActive == False`:
   - Use legacy method: Existing 3-prompt generation (headline + summary + article separately)
   - No changes to existing logic
5. Both paths save to `news_stories` collection with same schema
6. Logging clearly indicates which method used: "Using NEW method (isActive=true)" or "Using LEGACY method (isActive=false)"
7. Support both OpenAI and Claude providers (check config.model_config.provider)
8. Error handling:
   - If new method fails, log error but don't fall back to legacy (fail explicitly)
   - If legacy method fails, follow existing error handling
9. Backward compatibility verified:
   - Existing triggers without `isActive` field default to legacy method
   - Existing triggers with `isActive=false` use legacy method
10. Integration test: Run end-to-end generation for trigger with isActive=true and verify uses new method

### Story 1.16: Generation History UI (Frontend)

**As a** content manager,
**I want** to view history of all preview and production generations,
**so that** I can track testing iterations and review past results.

**Acceptance Criteria**:
1. Next.js page created: `app/history/page.tsx`
2. Filters:
   - Trigger name (dropdown)
   - Stock ID (number input)
   - Date range (date pickers)
   - Prompt type (checkboxes: Paid, Unpaid, Crawler)
   - Status (All, Preview, Production)
3. Table view (Bootstrap Table):
   - Columns: Timestamp | Trigger | Stock ID | Prompt Type | Model | Tokens | Cost | Status | Actions
   - Sortable by timestamp (default: newest first)
   - Pagination (20 per page)
4. Row expansion:
   - Click row to expand and show:
     - Generated title, summary, article (collapsible)
     - Full metadata: generation time, data mode used, sections included
     - "View Configuration" link (opens read-only config view)
5. "Preview" action button per row:
   - Opens modal with full article display
   - Formatted HTML rendering
   - Copy to clipboard button
6. Fetches data from: `GET /api/history?trigger_name={name}&stockid={id}&start_date={date}&end_date={date}&prompt_type={type}`
7. No caching: Always fetch fresh history (query MongoDB generation_history collection)
8. Export functionality:
   - "Export to CSV" button downloads filtered results
   - Includes all metadata columns
9. Empty state: "No generation history found for these filters"
10. Meets FR24, FR34: Track generation history with detailed metadata

### Story 1.17: Version Control & Rollback UI (Frontend)

**As a** content manager,
**I want** to view configuration version history and rollback to previous versions,
**so that** I can recover from mistakes or compare historical approaches.

**Acceptance Criteria**:
1. Next.js page created: `app/versions/[trigger_name]/page.tsx`
2. Version list view (timeline layout):
   - Each version displayed as card with:
     - Version number (v1, v2, v3...)
     - Published date and time
     - Published by (user name)
     - Status: Active (green badge) or Inactive (gray badge)
     - Data mode, model, prompt types used
   - Click card to expand full configuration details
3. **Expanded View** (per version):
   - Data Config: data_mode, sections, section_order
   - Model Config: provider, model, temperature, max_tokens
   - Prompts: All 3 types (paid/unpaid/crawler) with character count
   - "View Full Prompt" expandable sections
4. **Diff View**:
   - "Compare Versions" button
   - Select two versions from dropdowns
   - Side-by-side diff showing:
     - Added lines (green highlight)
     - Removed lines (red highlight)
     - Changed lines (yellow highlight)
   - Diff for prompts, data config, model config
5. **Rollback Functionality**:
   - "Rollback to This Version" button on inactive versions
   - Opens confirmation modal:
     - Warning: "Current production config (v5) will be replaced"
     - Summary of version being restored
     - Input: "Rollback reason" (text field for audit)
   - "Confirm Rollback" button
   - Calls `POST /api/config/rollback/{trigger_name}/{version}`
   - Backend creates new version (v6) with content from v3 (true rollback, not revert)
   - Audit log entry created
   - Success notification: "Rolled back to v3 as new version v6"
6. Fetches data from: `GET /api/versions/{trigger_name}`
7. Version metadata includes:
   - Test generation count (how many previews before publish)
   - Average cost per generation (from test history)
   - Number of iterations in testing phase
8. "Restore as Draft" option (alternative to rollback):
   - Loads old version into editor without publishing
   - Allows editing before republishing
9. Meets FR27, FR34: Versioning and history maintenance
10. Audit trail link per version: "View Changes" opens audit log filtered to that version

### Story 1.18: Testing & Documentation

**As a** QA engineer and future developer,
**I want** comprehensive test coverage and documentation for the News CMS Workflow,
**so that** the system is reliable and maintainable.

**Acceptance Criteria**:
1. **Backend Unit Tests** (pytest):
   - `StructuredDataService`: Test stockid handling, section filtering, reordering
   - `DataMergeService`: Test all 3 data modes (old, new, old_new)
   - `NewsGenerationService`: Test adaptive routing (isActive flag logic)
   - `ClaudeNewsGenerator` & `OpenAINewsGenerator`: Mock API responses
   - All Pydantic models: Validation rules (data_mode, sections, etc.)
   - Target coverage: 80%+ for services
2. **Backend Integration Tests** (pytest with test database):
   - End-to-end flow: save config → publish → generate news → verify output
   - Test with both isActive=true and isActive=false (new vs legacy paths)
   - Test data merge scenarios with real MongoDB test data
   - Test subprocess execution (mock generate_full_report.py or use test version)
3. **Frontend Unit Tests** (Jest + React Testing Library):
   - Component tests: TriggerSelection, DataConfig, PromptConfig, ModelConfig, PreviewPublish
   - Context tests: WorkflowContext state management
   - Validation logic tests: stockid format, section selection, prompt placeholders
   - Target coverage: 70%+ for components
4. **Frontend Integration Tests** (Playwright or Cypress):
   - E2E test: Complete workflow from trigger selection → data config → prompt config → model config → preview → publish
   - Test with NEW data mode (section selection)
   - Test with OLD_NEW data mode (merged data)
   - Test multi-type prompts (paid + unpaid + crawler)
   - Verify API calls made correctly (stockid parameter present)
5. **API Contract Tests**:
   - Validate all endpoints match OpenAPI spec (auto-generated by FastAPI)
   - Test required parameters: stockid in trigger data API
   - Test error responses: 404, 400, 500
6. **Load Testing** (optional but recommended):
   - Simulate 5-10 concurrent users running workflow
   - Verify no caching issues for structured data
   - Test LLM API rate limiting
7. **Documentation**:
   - **API Documentation**: OpenAPI/Swagger auto-generated by FastAPI at `/docs`
   - **Architecture Diagram**: Visual diagram showing workflow steps, data flow, API interactions
   - **User Guide**: Step-by-step guide for content managers (screenshots optional)
   - **Developer Guide**: Setup instructions, architecture decisions, data models
   - **Deployment Runbook**: AWS deployment steps, environment variables, MongoDB setup
8. **Code Comments**:
   - All services have docstrings explaining purpose, parameters, return types
   - Complex logic (data merge, HTML extraction) has inline comments
9. **README Updates**:
   - Root README.md updated with News CMS Workflow Feature section
   - backend/README.md lists all new services and endpoints
   - frontend/README.md lists all new pages and components
10. Meets NFR12, NFR13: Test coverage and production quality

## Epic Success Criteria

1. ✅ Content manager can select trigger + stockid and see existing OLD data + prompts
2. ✅ Content manager can choose data mode (OLD / NEW / OLD_NEW) and configure sections
3. ✅ Content manager can create/edit independent prompts for paid, unpaid, crawler with pre-population
4. ✅ Content manager can select model (OpenAI/Claude) and generate preview for all checked types
5. ✅ Content manager can publish configuration that sets isActive=true
6. ✅ Automated news generation checks isActive flag and routes to new or legacy method
7. ✅ All APIs include stockid parameter where required (trigger data, structured data generation)
8. ✅ No caching for structured data (always fresh), caching only for static configs
9. ✅ Backward compatibility maintained: existing triggers without isActive use legacy method
10. ✅ 80%+ test coverage for backend services, 70%+ for frontend components

## Epic Dependencies

- **Epic 1 (Foundation)**: Must be completed - requires MongoDB, FastAPI, Next.js setup
- **Story 1.3 (UI Shell)**: Provides navigation and layout framework
- **Story 1.4 (Trigger Dashboard)**: Can be extended for workflow trigger selection

## Timeline Estimate

**Total: 8-10 weeks**

- Stories 1.4-1.5 (Database + Trigger APIs): 1 week
- Stories 1.6-1.7 (Structured Data + Merge): 2 weeks
- Stories 1.8-1.9 (Config APIs + Generation Service): 2 weeks
- Stories 1.10-1.12 (Frontend: Trigger, Data, Prompt): 2 weeks
- Stories 1.13-1.14 (Frontend: Model, Preview): 1 week
- Stories 1.15-1.16 (Integration + History): 1 week
- Stories 1.17-1.18 (Versions + Testing): 1 week

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| `generate_full_report.py` has undocumented dependencies | High | Technical spike in Story 1.6, test subprocess execution early |
| LLM API rate limiting during testing | Medium | Implement request queuing, use lower-cost models for testing |
| HTML extraction regex fails for some LLM outputs | Medium | Robust regex patterns, fallback to raw HTML, extensive testing |
| Market hours caching complexity | Low | Simple approach: no caching for structured data, accept fresh generation cost |
| Backward compatibility breaks existing triggers | High | Thorough testing with isActive=false, staged rollout, feature flag |
| Frontend state management becomes complex | Medium | Use React Context with clear separation of concerns, consider Zustand if needed |

## Notes

- **Python Script Integration**: `generate_full_report.py` assumed to be in `structured_report_builder/` directory, executable via subprocess
- **Claude API**: Using `claude-sonnet-4-5-20250929` model as specified in user files
- **OpenAI API**: Using `gpt-4o` or similar for OpenAI provider
- **MongoDB Schema**: Extend existing collections rather than create new ones (per user feedback)
- **No Google**: Google AI provider removed from scope (per user requirements)
