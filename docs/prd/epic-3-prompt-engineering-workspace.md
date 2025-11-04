# Epic 3: Prompt Engineering Workspace

**Goal**: Create the prompt editing environment where content managers craft and refine prompts using real data. This epic delivers the core creative workspace with section management, tabbed prompt editor for multiple types (paid, unpaid, crawler), syntax-highlighted editing, real-time validation, and preview capabilities—enabling rapid prompt iteration without developer dependency. **Note**: Section management is shared across all prompt types, but each type has its own independent prompt template accessible via tabs.

### Story 3.1: Section Reordering Interface (Shared Across All Prompt Types)

**As a** content manager,
**I want** to reorder data sections via drag-and-drop or numbered input,
**so that** I can control the sequence in which data appears in all prompt types (paid, unpaid, crawler).

**Acceptance Criteria**:
1. "Section Order" panel displays structured data sections in current order
2. Drag-and-drop functionality implemented using React DnD library or Bootstrap Sortable
3. Alternative numbered input allows typing new position (e.g., move section 3 to position 1)
4. Section order changes immediately reflected in UI without page reload
5. "Preview Data Structure" updates to show new section order in final JSON
6. Section order saved to Configuration in MongoDB when changed (auto-save or explicit save button)
7. Meets FR11 and FR12: reordering capability with preview of effects
8. Undo/redo support for section order changes (single-level undo sufficient for MVP)
9. Visual feedback during drag operation (highlighting drop zones)

### Story 3.2: Tabbed Prompt Editor with Syntax Highlighting

**As a** content manager,
**I want** a tabbed full-featured text editor for crafting prompts for each type (paid, unpaid, crawler) with syntax highlighting,
**so that** I can write complex prompts comfortably for different audiences and see placeholder references clearly.

**Acceptance Criteria**:
1. Monaco Editor component integrated into Configuration Workspace with tabbed interface
2. Tabs displayed horizontally: [Paid] [Unpaid] [Crawler] - showing only checked prompt types from Trigger Context Bar
3. Active tab highlighted with blue underline, inactive tabs shown in gray
4. Clicking a tab switches the editor content to that prompt type's template
5. Each prompt type maintains its own template, independent of other types
6. Prompt editor displays current prompt template for selected tab or blank template for new configurations
7. Syntax highlighting configured for prompt format (highlighting placeholders like `{{section_name}}` or `{data.field}`)
8. Line numbers, search/replace, and keyboard shortcuts (Ctrl+F, Ctrl+Z) available
9. Editor resizable or full-screen mode for extended editing sessions
10. Meets FR13, FR14, FR38: tabbed editor with syntax highlighting for multiple prompt types
11. Auto-save prompt changes to React Context every 5 seconds (debounced) per prompt type
12. Editor theme configurable (light/dark mode) based on user preference or system setting
13. Word count or character count displayed per prompt type (helpful for LLM token estimation)
14. Tab icons: 💰 Paid, 🆓 Unpaid, 🕷️ Crawler for visual clarity

### Story 3.3: Data Placeholder Validation (Per Prompt Type)

**As a** content manager,
**I want** real-time validation of data placeholders in my prompt for the selected tab,
**so that** I catch errors before generation and know which data fields are available for each prompt type.

**Acceptance Criteria**:
1. Prompt editor parses placeholders in real-time for the currently active tab (e.g., `{{section_name}}`, `{data.field}`)
2. Invalid placeholders (referencing non-existent sections or fields) underlined in red with hover tooltip error message
3. Valid placeholders show green checkmark or no error indicator
4. Autocomplete suggestions appear when typing `{{` showing available section names and fields (same for all types since data is shared)
5. Validation runs on every keystroke (debounced to avoid performance issues) for active tab only
6. Validation error summary panel displays list of all invalid placeholders found in current tab's prompt
7. Clicking error in summary highlights corresponding placeholder in editor
8. Meets FR13: real-time validation of placeholder references per prompt type
9. Helper documentation or info icon explains placeholder syntax and available data fields
10. Tab indicator shows validation status (warning icon if errors exist in that tab's prompt)

### Story 3.4: Prompt Preview with Data Substitution (Per Prompt Type)

**As a** content manager,
**I want** to preview my prompt with actual data substituted for placeholders for the selected prompt type,
**so that** I can see exactly what will be sent to the LLM before generating.

**Acceptance Criteria**:
1. "Preview Prompt" button triggers substitution of placeholders with actual structured data for currently active tab
2. Preview displayed in read-only panel (Bootstrap Card or Modal) showing final prompt text for selected prompt type
3. Placeholders replaced with real values from current structured data state (shared across all types)
4. Sections included in order defined by section reordering (shared across all types)
5. Missing data (placeholder references non-existent value) shown with placeholder in red or warning marker
6. Preview updates automatically when data, section order, or tab selection changes
7. Meets FR15: preview of final prompt with actual data substituted per prompt type
8. Preview displays estimated token count for LLM (approximate calculation based on character count)
9. "Copy to Clipboard" button allows copying previewed prompt for external testing
10. Preview includes metadata: stock ID, trigger name, prompt type (paid/unpaid/crawler), timestamp
11. Modal shows tabs to preview all checked prompt types if desired

### Story 3.5: Prompt Version History and Undo (Per Prompt Type)

**As a** content manager,
**I want** version history and undo capability for prompt changes per prompt type,
**so that** I can experiment freely and revert mistakes without losing work for each audience type.

**Acceptance Criteria**:
1. Prompt changes tracked in local history (React Context or local state) with timestamp per prompt type
2. "Undo" button (or Ctrl+Z) reverts to previous prompt version for currently active tab
3. "Redo" button (or Ctrl+Y) re-applies undone changes for currently active tab
4. Version history panel shows list of last 10 prompt versions per type with timestamp and character count
5. Clicking a version in history loads that prompt into editor for the corresponding prompt type
6. Meets FR16: version history and undo capability per prompt type
7. History persisted in browser sessionStorage to survive page refresh (within session) maintaining separate history per type
8. Clear indication of current version vs. historical versions
9. "Save as New Version" button allows explicitly checkpointing important prompt iterations per type
10. History dropdown or panel shows which prompt type's history is being displayed based on active tab
