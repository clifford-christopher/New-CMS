# Epic-by-Epic Implementation Roadmap

## Epic 1: Foundation & Core Infrastructure (Weeks 1-3)

**Goal**: Establish deployable "walking skeleton" with trigger management.

**Stories**:
1. ⚠️ **Story 1.5a** (IN PROGRESS): Third-Party API Setup
   - Complete API key acquisition (OpenAI, Anthropic, Google)
   - Store all keys in AWS Secrets Manager
   - Configure billing alerts
   - Run test-api-keys.py successfully
   - **Blockers**: Anthropic API approval (1-2 days), financial data API provider selection

2. ❌ **Story 1.1**: Project Setup and Monorepo Structure
   - Create frontend/ and backend/ directories
   - Initialize package.json (frontend) and requirements.txt (backend)
   - Configure TypeScript, ESLint, pytest
   - Create .gitignore, README.md
   - Both apps run locally (uvicorn, npm run dev)

3. ❌ **Story 1.2**: MongoDB Database Setup and Connection
   - Install MongoDB or configure Atlas
   - Create Pydantic models (Trigger, Configuration, User, AuditLog)
   - Establish Motor async connection in FastAPI
   - Health check endpoint: GET /api/health
   - Seed script populates sample triggers

4. ❌ **Story 1.3**: Basic UI Shell and Navigation
   - Next.js layout with Bootstrap 5 CSS
   - Navbar with logo, Dashboard link, user info
   - Footer
   - Responsive grid system tested at 1200px, 768px
   - Loading spinner component

5. ❌ **Story 1.4**: Trigger Management Dashboard
   - GET /api/triggers endpoint
   - Dashboard page with dropdown trigger selector
   - Quick stats cards (Total Triggers, Configured, Last Updated)
   - Recent Activity list
   - Navigate to /config/:triggerId on selection
   - Loads in <2 seconds (NFR1)

6. ❌ **Story 1.6**: AWS Deployment Setup for Staging Environment
   - Provision EC2 t3.medium for staging
   - Install MongoDB on dedicated EC2 or configure Atlas
   - Deploy FastAPI as systemd service (uvicorn)
   - Deploy Next.js (decision: SSR on EC2 OR static to S3+CloudFront)
   - Nginx reverse proxy with SSL (AWS Certificate Manager)
   - GitHub Actions CI/CD to staging
   - Health check accessible via HTTPS
   - **Dependencies**: Story 1.5a complete (secrets available)

**Epic 1 Exit Criteria**:
- All APIs secured in Secrets Manager
- Monorepo structure established
- MongoDB connected and seeded
- Trigger dashboard displays triggers
- Staging environment deployed and accessible
- CI/CD pipeline deploys on push to develop

## Epic 2: Data Pipeline & Integration (Weeks 4-6)

**Goal**: Build data retrieval and transformation pipeline.

**Stories**:
1. ❌ **Story 2.1**: API Configuration Interface
   - Configuration Workspace page (frontend)
   - Trigger Context Bar with Stock ID input + prompt type checkboxes
   - Section Selection Dropdown (14 hardcoded sections, 5 pre-selected by backend)
   - "Use This Data" button (enabled by default)
   - POST /api/triggers/:id/config/sections, DELETE endpoints

2. ❌ **Story 2.2**: Data API Integration Layer
   - Create data_adapters/ module
   - Base DataAPIAdapter abstract class
   - 2+ concrete adapters (depends on financial API provider selection - BLOCKER)
   - Retry logic, rate limiting, request logging
   - Unit tests with mocked HTTP responses

3. ❌ **Story 2.3**: Data Retrieval and Raw JSON Display
   - POST /api/triggers/:id/data/fetch endpoint
   - Fetch data from configured APIs in parallel
   - Return raw JSON per section
   - Frontend displays collapsible JSON panels with syntax highlighting
   - Status indicators (success/failure, latency)
   - Completes within 5 seconds per API (NFR2)

4. ❌ **Story 2.4**: Parser Integration and Execution
   - Create parsers/adapter.py
   - Support module import OR subprocess execution (depends on parser investigation - BLOCKER)
   - POST /api/triggers/:id/data/parse endpoint
   - Parser timeout mechanism (10 seconds default)
   - Graceful error handling with actionable messages
   - Unit tests with sample JSON inputs

5. ❌ **Story 2.5**: Structured Data Display and Section Preview
   - Frontend displays parsed sections in Bootstrap Cards
   - Collapsible sections
   - Visual mapping (which API → which section)
   - "Preview Final Data Structure" button → JSON modal
   - Data persists in React Context for use in prompts

**Epic 2 Exit Criteria**:
- Section selection dropdown works with default selections
- Data fetched from APIs and displayed as raw JSON
- Parser executes and transforms data to structured sections
- Structured data displayed with clear labels
- Data available for prompt substitution

**Epic 2 Blockers**:
- Financial data API providers must be identified (product team decision)
- Parser script locations and interfaces must be documented

## Epic 3: Prompt Engineering Workspace (Weeks 7-9)

**Goal**: Create prompt editing environment with multi-prompt type support.

**Stories**:
1. ❌ **Story 3.1**: Section Reordering Interface (Shared Across All Prompt Types)
   - "Section Management" panel
   - Displays only selected sections from Data Configuration
   - Drag-and-drop sortable list (React DnD)
   - Number input alternative for accessibility
   - "Preview Data Structure" button
   - Section order saved to MongoDB

2. ❌ **Story 3.2**: Tabbed Prompt Editor with Syntax Highlighting
   - Monaco Editor component integrated
   - Tabbed interface: [💰 Paid] [🆓 Unpaid] [🕷️ Crawler]
   - Tab visibility controlled by Trigger Context Bar checkboxes
   - Paid tab always visible and active by default
   - Each tab maintains independent template and undo/redo stack
   - Syntax highlighting for placeholders ({{variable}})
   - Word/character count per tab
   - Auto-save every 5 seconds (debounced) per prompt type

3. ❌ **Story 3.3**: Data Placeholder Validation (Per Prompt Type)
   - Real-time parsing of placeholders for active tab only
   - Invalid placeholders underlined in red with tooltips
   - Valid placeholders show green checkmark
   - Autocomplete suggestions when typing {{
   - Validation error summary panel with line numbers
   - Tab indicator shows warning icon if errors in that tab's prompt

4. ❌ **Story 3.4**: Prompt Preview with Data Substitution (Per Prompt Type)
   - "Preview Final Prompt" button for active tab
   - Modal displays final prompt with actual data substituted
   - Missing data shown with red placeholder warning
   - Preview updates automatically when data/section order/tab changes
   - Estimated token count displayed
   - "Copy to Clipboard" button
   - Modal can show tabs to preview all checked prompt types

5. ❌ **Story 3.5**: Prompt Version History and Undo (Per Prompt Type)
   - Prompt changes tracked in local history per tab
   - Undo/Redo buttons (Ctrl+Z, Ctrl+Y) per tab
   - Version history panel shows last 10 versions per prompt type
   - Clicking version loads that prompt into editor for corresponding type
   - History persisted in sessionStorage (separate per type)
   - "Save as New Version" button for checkpointing per type

**Epic 3 Exit Criteria**:
- Sections can be reordered (only selected sections shown)
- Tabbed prompt editor works with 3 independent prompt types
- Placeholder validation catches errors per tab
- Prompt preview shows final prompt with data substituted per type
- Version history tracks changes per prompt type

## Epic 4: Multi-Model Generation & Testing (Weeks 10-12)

**Goal**: Implement LLM integration and multi-model testing workflow.

**Stories**:
1. ❌ **Story 4.1**: LLM Abstraction Layer and Provider Integration
   - Create llm_providers/ module
   - Base LLMProvider abstract class
   - OpenAI, Anthropic, Google AI concrete implementations
   - API authentication from AWS Secrets Manager
   - Cost calculation logic per provider
   - Rate limiting, retry logic
   - Provider registry for dynamic lookup
   - Unit tests with mocked API responses
   - Integration tests against real APIs (low-cost models)

2. ❌ **Story 4.2**: Model Selection Interface (Shared Across All Prompt Types)
   - "Model Selection" panel with header "(Used for All Types)"
   - Model cards grouped by provider (OpenAI, Anthropic, Google)
   - Checkboxes for model selection
   - Settings: temperature slider, max tokens input
   - **Cost estimate**: (selected models × checked prompt types)
   - Example: "2 models × 3 prompt types = 6 generations total"
   - Visual indicator: "Will generate for: Paid, Unpaid, Crawler"
   - Model selection saved to Configuration

3. ❌ **Story 4.3**: Parallel News Generation (For Checked Prompt Types)
   - POST /api/triggers/:id/generate endpoint
   - Backend initiates parallel LLM API calls using asyncio
   - Calculation: models × checked prompt types = total API calls
   - Frontend displays real-time status indicators (SSE or polling)
   - Status grouped by prompt type → model (Pending, Generating, Complete, Failed)
   - Progress: "Generating 4 of 6 complete"
   - Completes within 30 seconds timeout per model (NFR3)
   - Failed generations show error without blocking others
   - Results stored in generation_history collection

4. ❌ **Story 4.4**: Grouped Result Comparison (By Prompt Type → Model)
   - "Results & Comparison" panel
   - **Hierarchical Display**: Prompt Type Groups (collapsible) → Model Columns (side-by-side)
   - **Group 1**: 💰 Paid Prompt Results (blue header #0d6efd)
     - Side-by-side model columns (2-3 models)
     - Each result: model name, generated text, metadata
   - **Group 2**: 🆓 Unpaid Prompt Results (green header #198754)
     - Same layout as Group 1
   - **Group 3**: 🕷️ Crawler Prompt Results (orange header #fd7e14)
     - Same layout as Group 1
   - Metadata per result: 🎯 Tokens: 456 | ⏱️ Time: 8.3s | 💰 Cost: $0.08 (actual values)
   - Responsive: 2-3 columns on desktop, stacked on tablet
   - Visual outlier indicators within each group
   - "Copy" button per result

5. ❌ **Story 4.5**: Iterative Refinement Workflow
   - "Regenerate" button (regenerates for checked types and selected models)
   - Inline prompt editing available after results
   - "What Changed" tooltip shows diff between iterations
   - Iteration history timeline (collapsible, below results)
   - Timeline shows: iteration number, timestamp, which prompt types tested, changes made
   - Clicking historical generation loads that config and results
   - Debounced auto-save prevents losing changes
   - Quick cycle: edit → regenerate → compare in <60 seconds

6. ❌ **Story 4.6**: Post-Generation Metadata Display
   - Metadata container below each result card
   - Label: "⚡ ACTUAL METRICS" (subtle background #f8f9fa)
   - 🎯 Tokens Used: actual token count from LLM API
   - ⏱️ Time Taken: generation time in seconds (8.3s)
   - 💰 Actual Cost: calculated from actual tokens ($0.08)
   - Visual comparison: estimated vs. actual cost (diff indicator)
   - Performance indicators: green (<5s), yellow (5-15s), red (>15s)
   - Total cost summary: "Total actual cost: $0.48 (6 generations)"
   - Tooltip breakdown: "Prompt tokens: 234, Completion tokens: 222, Total: 456"

**Epic 4 Exit Criteria**:
- LLM providers integrated (OpenAI, Anthropic, Google)
- Model selection interface shows cost estimate: (models × prompt types)
- Parallel generation works for all checked prompt types
- Results displayed hierarchically: Prompt Type → Models
- Actual metadata (tokens, time, cost) shown per result
- Iteration workflow allows rapid testing

## Epic 5: Configuration Publishing & Production Integration (Weeks 13-14)

**Goal**: Enable publishing to production with validation and audit trails.

**Stories**:
1. ❌ **Story 5.1**: Pre-Publish Validation (All Prompt Types)
   - "Publish" button triggers validation for all 3 prompt types
   - Validation rules:
     - Shared: at least one API, section order defined, model selected
     - Per type: prompt not empty, at least one test generation for each checked type
   - Validation failure modal with checklist grouped by type
   - Warning if prompt changed without re-testing
   - Validation success enables "Confirm Publish" button

2. ❌ **Story 5.2**: Configuration Publishing with Confirmation (All Prompt Types)
   - Confirmation modal shows:
     - Trigger name
     - Configured APIs, section order, model (shared)
     - Per prompt type: truncated preview, character count, last tested timestamp
   - Expandable sections per type to view full prompt
   - Diff view if updating existing config (shows changes per type)
   - POST /api/triggers/:id/publish endpoint
   - Backend saves configuration to MongoDB with version number
   - Configuration marked as is_active = true
   - Success notification: "Published successfully with 3 prompt types as Version X.X"
   - "View Published Configuration" link

3. ❌ **Story 5.3**: Audit Logging and Change Tracking
   - All config changes logged to audit_log collection
   - Logged fields: user_id, action, timestamp, trigger_id, details (JSON diff)
   - Actions: created, updated, published, api_added, prompt_edited, model_changed
   - Backend middleware logs all write operations
   - Audit log UI (admin page, optional for MVP):
     - Table: timestamp, user, trigger, action, details
     - Filtering by trigger, user, date range, action
     - Export to CSV/JSON
   - Audit logs immutable (no deletion)

4. ❌ **Story 5.4**: Configuration Version History and Rollback
   - "Configuration History" screen (side-drawer)
   - List all published versions: version number, timestamp, user, "Active" badge
   - Click version → read-only view (APIs, prompt, model, section order)
   - "Compare with Another Version" button
   - Diff view: side-by-side comparison with highlighted changes
   - "Rollback to This Version" button
   - Rollback confirmation modal with warning
   - Rollback creates new version (not true revert)
   - Audit log entry created for rollback

5. ❌ **Story 5.5**: Production Integration and Active Configuration API
   - GET /api/triggers/:id/active-config endpoint
   - Returns currently active published configuration (all 3 prompt types)
   - Response includes: APIs, parser settings, section order, prompts (paid/unpaid/crawler), model config
   - API versioned (/api/v1/)
   - Cookie authentication required
   - Response cached (5-minute TTL)
   - 404 if no active config
   - OpenAPI documentation auto-generated
   - Integration test validates published config immediately accessible

**Epic 5 Exit Criteria**:
- Validation prevents publishing incomplete configs
- Publish confirmation shows all 3 prompt types with diff
- Audit log tracks all changes
- Version history accessible with rollback capability
- Active configuration API ready for existing news system integration
