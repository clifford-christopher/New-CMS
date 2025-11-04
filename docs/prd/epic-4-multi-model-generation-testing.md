# Epic 4: Multi-Model Generation & Testing

**Goal**: Implement the LLM integration layer and multi-model testing workflow that enables content managers to generate news using multiple AI models in parallel, compare outputs side-by-side, iterate rapidly, and track costs. This epic delivers the core AI functionality that transforms the CMS from a configuration tool into a powerful testing environment. **Note**: Model selection is shared across all prompt types—selected models will generate news for all checked prompt types. Generation results are grouped by prompt type → model for clear comparison.

### Story 4.1: LLM Abstraction Layer and Provider Integration

**As a** developer,
**I want** a unified abstraction layer for multiple LLM providers,
**so that** the system can easily support OpenAI, Anthropic, and Google models with consistent interfaces.

**Acceptance Criteria**:
1. Python module `llm_providers/` created with base `LLMProvider` abstract class defining interface (generate method)
2. Concrete implementations for OpenAI (GPT-4, GPT-3.5-turbo), Anthropic (Claude 3), Google (Gemini Pro)
3. Each provider adapter handles API authentication using keys from AWS Secrets Manager
4. Provider adapters normalize responses to common format: generated_text, token_count, model_name, latency, cost
5. Cost calculation logic implemented for each provider (using published pricing, tokens * price_per_token)
6. Rate limiting and retry logic implemented at provider level
7. All LLM API calls logged with prompt (truncated for logs), model, tokens, cost, latency
8. Unit tests with mocked API responses validate each provider adapter
9. Integration tests against real APIs (rate-limited, low-cost models) validate end-to-end flow
10. Provider registry allows dynamic lookup by model identifier (e.g., "gpt-4", "claude-3-sonnet")

### Story 4.2: Model Selection Interface (Shared Across All Prompt Types)

**As a** content manager,
**I want** to select multiple LLM models for parallel testing with adjustable settings that will be used for all checked prompt types,
**so that** I can compare different models' outputs across different audience types before choosing the best configuration.

**Acceptance Criteria**:
1. "Model Selection" panel displays available models grouped by provider (OpenAI, Anthropic, Google) with header label "(Used for All Types)"
2. Each model shows checkbox for selection, model name, and brief description
3. Selected models display additional settings: temperature slider (0.0-1.0), max tokens input
4. Cost estimate displayed per model based on average prompt size and configured max tokens
5. Total estimated cost calculation: (models × checked prompt types) shown prominently with breakdown
6. Example: 2 models × 3 prompt types (paid, unpaid, crawler) = 6 generations total
7. Default settings pre-configured (temperature=0.7, max_tokens=500) but user-adjustable
8. Meets FR17 and FR18: model selection with settings and cost estimates
9. At least one model must be selected to enable "Generate News" button
10. Model selection and settings saved to Configuration for reuse across all prompt types
11. Help tooltips explain temperature and max tokens parameters for non-technical users
12. Visual indicator shows "Will generate for: Paid, Unpaid, Crawler" based on checked types

### Story 4.3: Parallel News Generation (For Checked Prompt Types)

**As a** content manager,
**I want** to generate news using selected models for all checked prompt types in parallel with real-time status updates,
**so that** I can quickly test multiple approaches across different audiences without waiting sequentially.

**Acceptance Criteria**:
1. "Generate News" button triggers backend endpoint `POST /api/triggers/:id/generate` with selected models, checked prompt types, and corresponding prompts
2. Backend initiates parallel LLM API calls using Python asyncio (FastAPI async endpoint) for each (model × prompt type) combination
3. Example: 2 models × 2 types (paid, unpaid) = 4 parallel API calls
4. Frontend displays real-time generation status indicators grouped by prompt type, then by model (Pending, Generating, Complete, Failed)
5. Status updates delivered via Server-Sent Events (SSE) or polling (every 2 seconds) with prompt type and model identifiers
6. Meets FR19 and FR20: parallel generation across selected models and checked prompt types with real-time status
7. Loading spinner or progress bar shown during generation with count: "Generating 4 of 6 complete"
8. Generation completes within NFR3: 30 seconds timeout per model (configurable)
9. Failed generations display error message (API error, timeout) without blocking successful ones, clearly indicating which type and model failed
10. Results stored in MongoDB generation_history collection with timestamp, prompt per type, models, outputs per type
11. Session-level generation history allows navigating back to previous results with prompt type context

### Story 4.4: Grouped Result Comparison (By Prompt Type → Model)

**As a** content manager,
**I want** to view generated news grouped by prompt type then by model,
**so that** I can easily compare quality, tone, and accuracy across different audiences and select the best model for each type.

**Acceptance Criteria**:
1. "Generation Results" section displays outputs grouped hierarchically: Prompt Type → Models
2. Each prompt type section has colored header: 💰 Paid (blue), 🆓 Unpaid (green), 🕷️ Crawler (orange)
3. Within each prompt type, models displayed side-by-side in columns (2-3 columns on desktop)
4. Each model column shows: model name, generated news text, metadata (tokens, actual cost, latency)
5. Metadata displayed below each result: 🎯 Tokens: 456 | ⏱️ Time: 8.3s | 💰 Cost: $0.08
6. Columns aligned vertically within each prompt type group for easy visual comparison
7. Responsive design: 2-3 columns on desktop (1200px+), single column (stacked) on tablet (768-1199px)
8. Meets FR21 and FR22: grouped display by type with detailed metadata per generation
9. Syntax highlighting or formatting for generated text (markdown rendering if applicable)
10. "Copy" button per result allows copying generated news to clipboard
11. Visual indicators for outliers within each prompt type group: longest/shortest output, highest/lowest cost, fastest/slowest generation
12. Collapsible sections per prompt type to reduce scrolling when viewing multiple types
13. Meets NFR6: responsive design works on desktop and tablet
14. Results remain visible while editing prompt for iterative refinement
15. Meets FR40: actual token usage, generation time, and cost displayed prominently per result

### Story 4.5: Iterative Refinement Workflow

**As a** content manager,
**I want** to edit data or prompts and quickly regenerate to test variations,
**so that** I can rapidly iterate toward optimal news output.

**Acceptance Criteria**:
1. After initial generation, "Regenerate" button allows re-running generation with current prompt/data
2. Inline prompt editing in editor immediately available after viewing results (no mode switching)
3. Changes to prompt, data, or model selection highlighted visually (diff indicator or warning)
4. "What Changed" tooltip or panel shows diff between current and last generation configuration
5. Meets FR23 and FR24: inline editing with regeneration and change tracking
6. Generation history within session displays timeline of iterations (numbered: Generation 1, 2, 3...)
7. Clicking historical generation loads that configuration and results into view
8. Iteration count and timestamp displayed for each generation
9. Debounced auto-save prevents losing prompt changes during iteration
10. Quick iteration cycle: edit prompt → click regenerate → see new results in <60 seconds total

### Story 4.6: Post-Generation Metadata Display

**As a** content manager,
**I want** to see actual token usage, generation time, and cost for each model after generation completes,
**so that** I can make informed decisions about model selection based on performance and cost efficiency.

**Acceptance Criteria**:
1. After generation completes, metadata displayed below each model result card
2. Metadata shows three key metrics with icons:
   - 🎯 Tokens Used: Actual token count returned by LLM API
   - ⏱️ Time Taken: Generation time in seconds (e.g., 8.3s)
   - 💰 Actual Cost: Calculated cost based on actual tokens used (e.g., $0.08)
3. Metadata container has subtle background color (#f8f9fa) to distinguish from estimate
4. Label "GENERATION METRICS" or "⚡ ACTUAL METRICS" indicates post-generation data
5. Cost updates from estimated (shown before generation) to actual (shown after)
6. Visual comparison available: estimated cost vs. actual cost shown side-by-side or with diff indicator
7. Meets FR40: displays actual token usage, generation time, and cost per model per prompt type
8. Metadata persists in session and displayed when viewing historical generations
9. Total cost summary shown at bottom: "Total actual cost: $0.48 (6 generations)"
10. Export or copy functionality includes metadata for reporting purposes
11. Metadata tooltip provides breakdown: "Prompt tokens: 234, Completion tokens: 222, Total: 456"
12. Performance indicators: green (fast/<5s), yellow (medium 5-15s), red (slow/>15s) for time taken
