# Epic 2: Data Pipeline & Integration

**Status**: ✅ **Implemented** (Updated November 2025 for v2.3 workflow)

**Goal**: Build the complete data retrieval and transformation pipeline that connects to external data APIs, executes parser scripts, and displays structured data. This epic enables content managers to configure which data sources feed into news generation and preview the actual data that will be used in prompts—addressing the critical pain point of "no visibility into data." **Note**: Data configuration is shared across all three prompt types (paid, unpaid, crawler) for consistency and efficiency.

**v2.3 Update**: Story 2.5 now covers section SELECTION (with checkboxes) in Data Configuration tab. Section ORDERING moved to Story 3.1 (Section Management tab).

### Story 2.1: API Configuration Interface

**As a** content manager,
**I want** to add and remove data APIs from a trigger's configuration,
**so that** I can control which data sources are used for news generation.

**Acceptance Criteria**:
1. Configuration Workspace page loads trigger details from `GET /api/triggers/:id/config` (includes currently configured APIs)
2. "Data Sources" panel displays list of currently configured APIs with remove button for each
3. "Add API" dropdown or modal shows predefined list of available data APIs (from backend registry or database)
4. Clicking "Add API" sends `POST /api/triggers/:id/config/apis` with API identifier, updates UI optimistically
5. Clicking "Remove" button sends `DELETE /api/triggers/:id/config/apis/:apiId`, updates UI
6. Backend validates that required APIs are present before allowing removal (FR5)
7. Changes auto-save to MongoDB Configuration collection
8. Toast notification confirms successful add/remove operations
9. Error handling prevents adding duplicate APIs and displays clear error message

### Story 2.2: Data API Integration Layer

**As a** developer,
**I want** a flexible adapter layer for integrating external data APIs,
**so that** the system can fetch financial data from multiple sources reliably.

**Acceptance Criteria**:
1. Python module `data_adapters/` created with base `DataAPIAdapter` abstract class defining interface (fetch_data method)
2. At least two concrete adapter implementations (e.g., `EarningsAPIAdapter`, `PriceDataAPIAdapter`)
3. Each adapter handles API authentication (API keys from environment variables or Secrets Manager)
4. Adapters implement retry logic with exponential backoff for transient failures (503, timeout)
5. Adapters implement rate limiting to respect API quotas (using Python ratelimit library)
6. All API calls logged with request URL, response status, and latency
7. Adapter registry pattern allows dynamic lookup of adapters by API identifier
8. Unit tests for adapter logic with mocked HTTP responses (using httpx Mock or responses library)
9. Integration tests against sandbox/test endpoints or mocked APIs validate error handling (404, 500, timeout)

### Story 2.3: Data Retrieval and Raw JSON Display

**As a** content manager,
**I want** to fetch and view raw JSON data from configured APIs for a specific stock,
**so that** I understand exactly what data is being retrieved.

**Acceptance Criteria**:
1. Configuration Workspace includes stock ID input field with "Fetch Data" button
2. Backend endpoint `POST /api/triggers/:id/data/fetch` accepts stock ID and returns raw JSON from all configured APIs
3. Frontend displays loading indicator during data fetch (meets NFR2: completes within 5 seconds per API)
4. Raw JSON displayed in collapsible panels (one per API) with syntax highlighting (JSON formatting)
5. Each API panel shows: API name, fetch status (success/failure), latency, timestamp
6. Failed API calls display error message (timeout, 404, 500) without blocking other APIs
7. Success state shows formatted JSON with expand/collapse capability for nested objects
8. "Refresh Data" button allows re-fetching without re-entering stock ID
9. Stock ID validation checks format before allowing fetch (prevents invalid requests)
10. Meets FR6 and FR7: organized display with status indicators

### Story 2.4: Parser Integration and Execution

**As a** developer,
**I want** to execute existing parser scripts that transform raw API data into structured format,
**so that** data can be organized into sections for prompt generation.

**Acceptance Criteria**:
1. Python module `parsers/` contains adapter layer for existing parser scripts
2. Parser execution supports two modes: direct module import (if parsers are Python modules) or subprocess calls (if standalone scripts)
3. Backend endpoint `POST /api/triggers/:id/data/parse` accepts raw JSON and returns structured data sections
4. Parsers receive raw API data as JSON input and return structured output with sections (e.g., "Earnings Summary", "Price History")
5. Parser errors (exceptions, non-zero exit codes) caught and returned with actionable error messages (FR10)
6. Timeout mechanism (configurable, default 10 seconds) prevents hanging on parser failures
7. Parsed output logged for debugging and audit purposes
8. Unit tests validate parser execution with sample JSON inputs and expected outputs
9. Integration tests cover error scenarios: malformed JSON, missing required fields, parser script failures

### Story 2.5: Section Selection and Data Preview in Data Configuration

**As a** content manager,
**I want** to SELECT which data sections to use (with checkboxes) and preview them in the Data Configuration step,
**so that** I can choose relevant sections before proceeding to section ordering.

**Purpose**: This story covers the SELECTION phase - users choose which sections to include. The ORDERING phase happens in Story 3.1 (Section Management).

**Acceptance Criteria**:

**Data Fetch/Generation (Step 1)**:
1. **OLD Mode**: "Fetch Data" button retrieves existing trigger data from `news_triggers` collection
2. **NEW Mode**: "Generate Complete Report" button generates all 14 sections using structured_report_builder
3. **OLD_NEW Mode**: Fetches OLD data + generates NEW data (both operations)
4. Loading indicator displays during data fetch/generation with estimated time (8-15 seconds for NEW)
5. Cached data notification shown if data already exists for current stock ID
6. Error handling displays clear messages if data fetch/generation fails

**Section Selection UI (Step 2 - NEW/OLD_NEW modes only)**:
7. **NEW Mode**: After generation, displays all 14 sections with checkboxes
   - Each section card shows: Checkbox | Section number badge | Section title | Expand/collapse button
   - Checkbox click selects/deselects section
   - Visual highlight: Selected sections have blue border and light blue background
   - **View Toggle Buttons**: "All Sections" (shows all 14) | "Selected Only" (filters to checked only)
   - **Bulk Selection Buttons**: "Select All" | "Clear All"
   - Selected count indicator: "5 sections selected" (updates dynamically)
8. **OLD_NEW Mode**: Shows two panels:
   - OLD Data preview (OldDataDisplay component - read-only JSON view)
   - NEW sections with checkboxes (NewDataDisplay component - same as NEW mode)
9. **OLD Mode**: Shows OLD data preview only (no selection needed)
   - OldDataDisplay component with read-only JSON view
   - Info alert: "This entire data structure will be treated as one section"

**Section Preview**:
10. Each section displayed in Bootstrap Card with collapsible content
11. Section content formatted appropriately (JSON, text, nested objects)
12. Expand/collapse functionality allows focusing on specific sections
13. Empty sections display placeholder: "No data available for this section"
14. **Data Source Badges**:
    - OLD data: Blue "OLD" badge (info variant)
    - NEW data: Green "NEW" badge (success variant)

**"Use This Data" Button (Step 3)**:
15. **OLD Mode**: Button enabled immediately after data fetch, labeled "Use This Data"
16. **NEW Mode**: Button enabled when selections > 0, labeled "Use This Data (X sections)"
17. **OLD_NEW Mode**: Button enabled when NEW selections > 0, labeled "Use This Data (OLD + X NEW sections)"
18. Button click action: Navigates to Section Management tab (activeStep = 'sections')
19. Button styling: Primary blue, 300-350px width, checkmark icon

**Data Persistence**:
20. Uses localStorage/sessionStorage with keys:
    - `fetchedOldData_{triggerId}`: Stores fetched OLD data
    - `generatedNewData_{triggerId}`: Stores generated NEW sections (all 14)
    - `selectedSectionIds_{triggerId}`: Stores user's selected section IDs
21. Data cached by stock ID - prevents regeneration when stock ID unchanged
22. Cache cleared on explicit trigger change or stock ID change
23. Selected sections preserved in React state for passing to Section Management

**Section Selection Logic**:
24. OLD mode: No selection needed, passes `{id: 'old_data', name: 'OLD Data (Complete)', source: 'old'}` to Section Management
25. NEW mode: Passes selectedSectionIds array to Section Management (e.g., ["1", "3", "5", "9"])
26. OLD_NEW mode: Passes OLD section + selectedSectionIds to Section Management

**Validation**:
27. Cannot proceed to Section Management if NEW/OLD_NEW mode and no sections selected
28. Warning tooltip on disabled button explains requirement
29. Meets FR11: Section selection with checkboxes in Data Configuration step
30. Meets FR12: Preview of selected sections before proceeding

**Note**: This story focuses on SELECTION only. Section REORDERING happens in Story 3.1 (Section Management Panel).
