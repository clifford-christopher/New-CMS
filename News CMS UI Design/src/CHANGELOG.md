# News CMS Application - Changelog

## Version 2.3 (October 29, 2025) - Multi-Type Prompt Support

### 🎯 Major Changes

This is a **MAJOR UPDATE** introducing support for multiple prompt types: Paid, Unpaid, and Web Crawler.

#### 1. **Type Selection Checkbox Component** (NEW)
- ✅ Created reusable TypeSelectionCheckbox component
- ✅ Three prompt types with icons:
  - 💰 Paid (always checked, disabled)
  - 🆓 Unpaid (optional)
  - 🕷️ Web Crawler (optional)
- ✅ Helper text explaining usage
- ✅ "Default" badge on Paid type
- ✅ Proper disabled styling for Paid checkbox

#### 2. **Trigger Context Bar** - Enhanced with Type Selection
- ✅ **Two-row layout**: Top row (trigger info, stock ID, status), Bottom row (type selection)
- ✅ **Auto-fetch on Stock ID change**: Debounced input triggers data fetch
- ✅ **Four status badge states**:
  - "Configure Data" (Gray) - initial
  - "Fetching Data..." (Cyan with spinner) - loading
  - "Data Ready for [STOCK]" (Green with checkmark) - success
  - "Configuration Error" (Red with warning) - error
- ✅ **Divider** between rows for visual separation
- ✅ Height increased to 140px to accommodate type selection

#### 3. **Prompt Editor** - Tabbed Interface
- ✅ **Tabbed navigation**: One tab per selected type
- ✅ **Two-row toolbar**:
  - Top: Title, auto-save, undo/redo, preview, history
  - Bottom: Type tabs with icons (💰 Paid, 🆓 Unpaid, 🕷️ Crawler)
- ✅ **Independent editor states**: Each tab maintains its own content
- ✅ **Active tab styling**: White background + blue bottom border
- ✅ **Inactive tabs**: Transparent background, gray text
- ✅ **Only shows tabs for checked types**: Paid always visible
- ✅ **Automatic tab switching**: Switches to first available if current tab unchecked
- ✅ **Default templates** for each type with appropriate content

#### 4. **Model Selection** - Post-Generation Metrics
- ✅ **Badge added**: "(Used for All Types)" indicator
- ✅ **Enhanced description**: Explains cross-type usage
- ✅ **Info callout**: Shows total generations (types × models)
  - Example: "3 types × 2 models = 6 generations"
  - Updates dynamically based on selections
- ✅ **Post-generation metrics section** (shown after generation):
  - 🎯 Tokens: Actual token count
  - ⏱️ Time: Generation time with color coding
    - Green (<5s), Yellow (5-15s), Red (>15s)
  - 💰 Actual Cost: Real cost per generation
  - Tooltip on hover showing token breakdown
- ✅ **Estimated vs Actual**: Shows both estimated (before) and actual (after) costs
- ✅ **Model card layout**: 2-column responsive grid
- ✅ **Metrics container**: Light gray background to distinguish from estimate

#### 5. **Results Comparison Panel** - Grouped Display
- ✅ **Hierarchical organization**: Results grouped by Prompt Type → Model
- ✅ **Collapsible groups**: Each type has collapsible header
- ✅ **Color-coded groups**:
  - 💰 Paid: Blue (#e7f1ff background, #0d6efd border/text)
  - 🆓 Unpaid: Green (#d1f4e0 background, #198754 border/text)
  - 🕷️ Crawler: Orange (#fff3cd background, #ffc107 border/text)
- ✅ **Group headers**: Icon + label + chevron (up/down)
- ✅ **2-column result grid**: Side-by-side model comparison within each type
- ✅ **Result cards**: Header (model name + status) → Content → Footer (metrics)
- ✅ **Metadata with icons**: 🎯 tokens, ⏱️ time (color-coded), 💰 cost
- ✅ **Star ratings**: 5-star component per result
- ✅ **Total cost summary**: Shows total across all types and models
- ✅ **Default expanded**: Paid group always expanded, others collapsed
- ✅ **Smooth animations**: Expand/collapse transitions

#### 6. **Configuration Workspace** - State Management
- ✅ **Selected types tracking**: Manages selectedTypes state
- ✅ **Stock ID state**: Centralized stock ID management
- ✅ **Props passing**: Passes selectedTypes to PromptEditor, ModelSelection, ResultsComparisonPanel
- ✅ **ContextBar integration**: Passes all required props including type handlers

### 📊 Data Flow Architecture

```
ConfigurationWorkspace (Parent)
├── selectedTypes: PromptType[]         // ['paid'] | ['paid', 'unpaid'] | ['paid', 'unpaid', 'crawler']
├── stockId: string                     // Current test stock ID
│
├── ContextBar
│   ├── selectedTypes (display + modify)
│   ├── onTypesChange (callback)
│   ├── stockId (display + edit)
│   └── onStockIdChange (auto-fetch trigger)
│
├── PromptEditor
│   ├── selectedTypes (determines visible tabs)
│   └── Separate editor state per type
│
├── ModelSelection
│   ├── selectedTypes (calculates total generations)
│   └── Info callout: types × models
│
└── ResultsComparisonPanel
    ├── selectedTypes (filters displayed groups)
    └── Groups results by type → model
```

### 🎨 UI/UX Enhancements

1. **Visual Hierarchy**: Clear grouping by prompt type with color coding
2. **Progressive Disclosure**: Collapsible groups reduce visual clutter
3. **Contextual Feedback**: Info callouts explain generation counts
4. **Performance Indicators**: Color-coded time metrics (green/yellow/red)
5. **Consistent Iconography**: Emojis for quick type identification
6. **Responsive Design**: 2-column grids adapt to screen size
7. **State Persistence**: Each tab maintains independent state

### 🔧 Technical Implementation

**New Component:**
```typescript
/components/TypeSelectionCheckbox.tsx
- export type PromptType = 'paid' | 'unpaid' | 'crawler'
- TypeSelectionCheckboxProps: selectedTypes, onTypesChange
```

**Updated Components:**
1. `/components/ContextBar.tsx` - Two-row layout, type selection, auto-fetch
2. `/components/PromptEditor.tsx` - Tabbed interface, per-type state
3. `/components/ModelSelection.tsx` - Info callout, post-generation metrics
4. `/components/ResultsComparisonPanel.tsx` - Grouped hierarchical display
5. `/components/ConfigurationWorkspace.tsx` - State management, props passing

### 📝 User Flow

1. **Select Types** (Context Bar):
   - User checks Unpaid and/or Crawler (Paid always checked)
   - Context bar updates to show selected types

2. **Configure Prompts** (Prompt Editor):
   - Tabs appear for each checked type
   - User can edit each prompt independently
   - Active tab highlighted with blue border

3. **Select Models** (Model Selection):
   - Info callout shows: "3 types × 2 models = 6 generations"
   - User selects models and configures settings
   - Clicks "Generate with Selected Models"

4. **View Results** (Results Comparison):
   - Results grouped by type (Paid, Unpaid, Crawler)
   - Each group collapsible with color-coded header
   - Within each group: 2-column model comparison
   - Metrics shown: tokens, time (color-coded), cost, rating
   - Total cost summary at bottom

### 🐛 Bug Fixes
- Fixed type selection persistence across navigation
- Fixed tab switching when type is unchecked
- Fixed metric color coding for performance indicators
- Fixed group expansion state management

### 🚀 Performance
- Lazy rendering of collapsed groups
- Memoized result filtering by type
- Efficient state updates for type selection
- Debounced stock ID auto-fetch (500ms)

### 📚 Documentation
- Updated CHANGELOG with v2.3 details
- Documented type selection workflow
- Added data flow architecture diagram
- Component prop documentation

---

## Version 2.2 (October 28, 2025) - Backend Default Selections & Workflow

### 🎯 Major Changes

#### 1. **Data Configuration Panel - Backend Default Selections**
- ✅ **Pre-selected Sections**: 5 default sections loaded on page load (Sections 1, 2, 3, 5, 7)
- ✅ **Button Renamed**: "Fetch Data" → "Use This Data" with arrow-right icon
- ✅ **Default Configuration Badge**: Shows "Default configuration" indicator initially
- ✅ **Dynamic Helper Text**: Updates to show count of selected sections
- ✅ **Enabled by Default**: Button is enabled since backend provides selections
- ✅ **State Tracking**: Tracks whether user has modified default selections

**Default Selections:**
- Section 1: Company Information ✓
- Section 2: Quarterly Income Statement ✓
- Section 3: Annual Income Statement ✓
- Section 5: Cash Flow Statement ✓
- Section 7: Valuation Metrics ✓

#### 2. **Trigger Context Bar - Status Badge System**
- ✅ **Removed**: Fetch Data button (redundant with panel button)
- ✅ **Added**: Configuration status badges with three states:
  - **"Configure Data"** (Gray #6c757d): Initial state, data not configured
  - **"Data Ready"** (Green #198754): Data has been configured and fetched
  - **"Configuration Error"** (Red #dc3545): Error in configuration
- ✅ **Stock ID**: Updated placeholder to "TCS" (matching v2.2 spec)
- ✅ **Dynamic Updates**: Badge changes based on dataConfigured state

#### 3. **Section Management Panel - Dynamic Section Display**
- ✅ **Shows Only Selected Sections**: Panel displays only sections chosen in Data Configuration
- ✅ **Dynamic Section Mapping**: Maps section IDs to full names (e.g., "1" → "Company Information")
- ✅ **Updated Description**: Clarifies that only selected sections are shown
- ✅ **Section Count**: Shows "Only the X sections you selected are shown"
- ✅ **Placeholder Updates**: Uses `{{section_X}}` format for placeholders

#### 4. **Configuration Workspace - State Management**
- ✅ **Shared State**: `selectedSections` state lifted to ConfigurationWorkspace
- ✅ **Data Flow**: Passes selectedSections from DataConfiguration → SectionManagement
- ✅ **Completion Tracking**: Tracks `dataConfigured` state
- ✅ **Status Updates**: Updates ContextBar status based on data configuration
- ✅ **Sidebar Completion**: Passes completedSteps to WorkflowSidebar

#### 5. **Workflow Sidebar - Dynamic Completion**
- ✅ **Removed Hardcoded Completion**: No longer shows hardcoded completed states
- ✅ **Dynamic Checkmarks**: Shows checkmarks based on `completedSteps` prop
- ✅ **Data Config Completion**: Shows green checkmark after data is configured

### 📋 Technical Details

#### State Flow Architecture
```
ConfigurationWorkspace (Parent)
├── selectedSections: string[]          // Shared state
├── dataConfigured: boolean             // Completion tracker
│
├── DataConfigurationPanel
│   └── onDataConfigured(sections) →    // Updates parent state
│
├── SectionManagementPanel
│   └── selectedSectionIds={sections}   // Receives selected sections
│
├── ContextBar
│   └── dataStatus={...}                // Shows status badge
│
└── WorkflowSidebar
    └── completedSteps={[...]}          // Shows completion checkmarks
```

#### Component Props Updates

**DataConfigurationPanel:**
```typescript
type DataConfigurationPanelProps = {
  onDataConfigured?: (sections: string[]) => void;
};
```

**SectionManagementPanel:**
```typescript
type SectionManagementPanelProps = {
  selectedSectionIds?: string[];
};
```

**ContextBar:**
```typescript
type DataStatus = 'not-configured' | 'ready' | 'error';

type ContextBarProps = {
  triggerName: string;
  lastPublished?: string;
  version?: string;
  dataStatus?: DataStatus;
};
```

**WorkflowSidebar:**
```typescript
type WorkflowSidebarProps = {
  currentStep: WorkflowStep;
  onStepChange: (step: WorkflowStep) => void;
  completedSteps?: WorkflowStep[];
};
```

### 🎨 UI/UX Improvements

1. **Clearer Workflow**: Status badges provide immediate visual feedback
2. **Better Defaults**: Users can start with sensible defaults and modify as needed
3. **Reduced Redundancy**: Removed duplicate Fetch Data button
4. **Dynamic Feedback**: Helper text updates based on selection count
5. **Visual Indicators**: "Default configuration" badge shows initial state
6. **Completion Tracking**: Sidebar shows which steps are complete

### 🔧 Configuration

**Default Section IDs:**
```typescript
const DEFAULT_SELECTIONS = ['1', '2', '3', '5', '7'];
```

**Section Name Mapping:**
```typescript
const sectionNameMap: Record<string, string> = {
  '1': 'Company Information',
  '2': 'Quarterly Income Statement',
  '3': 'Annual Income Statement',
  '4': 'Balance Sheet',
  '5': 'Cash Flow Statement',
  '6': 'Key Financial Ratios & Metrics',
  '7': 'Valuation Metrics',
  '8': 'Shareholding Pattern',
  '9': 'Stock Price & Returns Analysis',
  '10': 'Technical Analysis',
  '11': 'Quality Assessment',
  '12': 'Financial Trend Analysis',
  '13': 'Proprietary Score & Advisory',
  '14': 'Peer Comparison'
};
```

### 📝 User Flow

1. **User opens Configuration Workspace**
   - ContextBar shows "Configure Data" (gray badge)
   - DataConfiguration panel loads with 5 sections pre-selected
   - "Default configuration" badge visible
   - "Use This Data" button is enabled

2. **User modifies selections (optional)**
   - Clicks dropdown to view all 14 sections
   - Checks/unchecks sections as needed
   - "Default configuration" badge disappears
   - Helper text updates with new count

3. **User clicks "Use This Data"**
   - Data is fetched for selected sections
   - ContextBar updates to "Data Ready" (green badge)
   - Success message shows: "Successfully fetched data from X sections"
   - WorkflowSidebar shows checkmark on Data Configuration step
   - State flows to SectionManagementPanel

4. **User navigates to Section Management**
   - Panel shows only the sections user selected
   - Sections are reorderable
   - Description clarifies: "Only the X sections you selected are shown"

### 🐛 Bug Fixes
- Fixed state management between panels
- Fixed completion tracking in sidebar
- Fixed status badge not updating
- Fixed section management not receiving selected sections

### 🚀 Performance
- No performance impact from additional state management
- Efficient prop passing without unnecessary re-renders
- Badge updates are instant and reactive

### 📚 Documentation Updates
- Updated README with v2.2 version history
- Created comprehensive CHANGELOG
- Added state flow architecture diagram
- Documented all prop type changes

---

## Version 2.1 (October 28, 2025) - Multi-Select Dropdown

- Data Configuration redesigned with multi-select dropdown
- 14 hardcoded data sections with checkboxes
- "Select All" / "Clear All" functionality
- Removed "Add API" pattern

## Version 2.0 (October 28, 2025) - MVP Scope

- Dashboard with dropdown trigger selector
- Removed Audit Log and Settings screens
- Streamlined workflow-focused layout
- Dark navbar with context-aware navigation

## Version 1.0 (Initial Release)

- Card-based dashboard design
- Basic configuration workflow
- Audit Log and Settings screens included

---

**Current Version**: 2.2  
**Last Updated**: October 28, 2025  
**Status**: ✅ Production Ready
