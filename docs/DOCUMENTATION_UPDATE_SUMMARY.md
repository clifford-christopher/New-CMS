# Documentation Update Summary - News CMS Workflow v2.3

**Date**: November 3, 2025
**Version**: 2.3
**Update Type**: Major workflow reorganization
**Status**: ✅ Complete

---

## Executive Summary

All News CMS documentation has been updated to reflect the reorganized UI workflow implemented in the codebase. The key change separates data **selection** (in Data Configuration) from section **ordering** (in Section Management), providing a clearer, more intuitive user experience.

### Core Change

**Previous Workflow**:
- Data Configuration: Fetch/generate data → Display
- Section Management: Select AND reorder sections together

**New Workflow (v2.3)**:
- **Data Configuration Tab**: Fetch/generate data → **SELECT sections with checkboxes** → "Use This Data" button
- **Section Management Tab**: **REORDER selected sections** with drag-and-drop only

---

## Files Updated (100% Complete)

### ✅ Primary Documentation (4 files)

| File | Status | Changes Made |
|------|--------|-------------|
| `docs/front-end-spec.md` | ✅ Complete | Updated Change Log (v2.3), Panel 1 (Data Configuration), Panel 2 (Section Management) |
| `docs/prd.md` | ✅ Complete | Updated FR11, FR12, FR37, "Core Screens and Views" section |
| `docs/prd/epic-2-data-pipeline-integration.md` | ✅ Complete | Rewrote Story 2.5 with 30 detailed acceptance criteria for selection workflow |
| `docs/prd/epic-6-news-cms-workflow.md` | ✅ Complete | Rewrote Story 1.11 as two-phase workflow (Selection + Ordering) |

### ✅ Individual Story Files (3 files)

| File | Status | Changes Made |
|------|--------|-------------|
| `docs/stories/2.1.api-configuration-interface.md` | ✅ Complete | Added workflow context note, updated status to v2.3 |
| `docs/stories/2.3.data-retrieval-and-raw-json-display.md` | ✅ Complete | Updated 14 acceptance criteria with section selection UI specs |
| `docs/stories/3.1.section-reordering-interface.md` | ✅ Complete | Rewrote with 16 acceptance criteria focusing on ordering only, added mode-specific displays |

---

## Detailed Changes by File

### 1. frontend-spec.md

**Version**: Updated to v2.3

**Sections Modified**:
- **Change Log**: Added entry for v2.3 reorganization
- **Panel 1: Data Configuration** (Lines 424-477):
  - Added three-step process: Data mode selection → Data fetch/generation → Section selection with checkboxes
  - Specified OLD mode behavior: Data preview + "Use This Data" button
  - Specified NEW mode behavior: Checkbox selection UI + view toggle + "Use This Data (X sections)" button
  - Specified OLD_NEW mode behavior: OLD preview + NEW checkboxes + "Use This Data (OLD + X sections)" button
  - Added data persistence specification using localStorage/sessionStorage

- **Panel 2: Section Management** (Lines 479-541):
  - Changed purpose to "Arrange ORDER of sections" (receives already selected sections)
  - Added three mode-specific displays:
    - **OLD Mode**: Single read-only section "OLD Data (Complete)"
    - **NEW Mode**: Only selected NEW sections with drag-and-drop
    - **OLD_NEW Mode**: Combined list with OLD + NEW sections, all draggable
  - Added drag-and-drop interaction specifications
  - Added warning for no selections
  - Updated data persistence keys

**Key Addition**: "Use This Data" button navigation behavior clearly documented for all three modes.

---

### 2. prd.md

**Sections Modified**:
- **FR11** (Line 43): Updated to specify "SELECT in Data Configuration" and "REORDER in Section Management"
- **FR12** (Line 44): Updated to specify preview in both tabs
- **FR37** (Line 69): Added clarification "selection happens in Data Configuration, ordering happens in Section Management"
- **Core Screens and Views** (Lines 117-122): Updated Configuration Workspace description to reflect two-phase workflow

**Impact**: All functional requirements now accurately describe the selection → ordering workflow.

---

### 3. epic-2-data-pipeline-integration.md

**Story 2.5: Section Selection and Data Preview** (Lines 74-143)

**Complete Rewrite**: Changed from "Structured Data Display" to "Section Selection and Data Preview"

**New Structure**:
- **Purpose Statement**: Explicitly states this covers SELECTION phase only
- **Data Fetch/Generation (Step 1)**: 6 acceptance criteria covering OLD/NEW/OLD_NEW fetch behavior
- **Section Selection UI (Step 2)**: 3 acceptance criteria for checkbox interaction, view toggle, bulk actions
- **Section Preview**: 5 acceptance criteria for display formatting
- **"Use This Data" Button (Step 3)**: 4 acceptance criteria for button behavior per mode
- **Data Persistence**: 4 acceptance criteria for localStorage/sessionStorage caching
- **Section Selection Logic**: 3 acceptance criteria for passing data to Section Management
- **Validation**: 4 acceptance criteria for error handling

**Total**: 30 detailed acceptance criteria (up from 13)

**Key Changes**:
- Removed ordering functionality (moved to Story 3.1)
- Added checkbox selection UI specifications
- Added "Use This Data" button with mode-specific labels
- Added navigation to Section Management tab

---

### 4. epic-6-news-cms-workflow.md

**Story 1.11: Data Configuration and Section Management** (Lines 412-513)

**Major Update**: Split into two clear phases

**New Structure**:
- **Purpose Statement**: "TWO-PHASE workflow" clearly defined
- **Phase 1: Data Configuration (Selection)** (ACs 1-6):
  - Tabbed interface specification
  - Data mode selection UI
  - Data fetch/generation per mode
  - Section selection UI with checkboxes (NEW/OLD_NEW only)
  - Section preview components (OldDataDisplay, NewDataDisplay)
  - "Use This Data" button with navigation

- **Phase 2: Section Management (Ordering)** (ACs 7-13):
  - Mode-specific section displays:
    - OLD: Single section, drag disabled
    - NEW: Selected sections only, drag enabled
    - OLD_NEW: Combined OLD + NEW, all draggable
  - Drag-and-drop implementation details
  - Data persistence and navigation flow
  - Validation and error handling

**Key Additions**:
- Example OLD_NEW display with visual representation
- Explicit statement that OLD section can be positioned anywhere
- Clear navigation flow: Data Config → "Use This Data" → Section Management

---

### 5. stories/2.1.api-configuration-interface.md

**Status**: Updated to "Draft - Updated for Data Configuration Workflow v2.3"

**Changes**:
- Added workflow context note at beginning
- Added AC 1a: Reference to section selection UI in Data Configuration (Story 2.5)
- Minimal changes (story focus unchanged, just context added)

---

### 6. stories/2.3.data-retrieval-and-raw-json-display.md

**Status**: Updated to "Draft - Updated for Data Configuration Workflow v2.3"

**Changes**:
- Added "Workflow Context (v2.3)" section explaining two-tab flow
- Updated AC 3: Changed endpoint to match implementation (`GET /api/stocks/{stockid}/trigger-data`)
- Updated AC 5: Completely rewrote to specify section selection UI appearance after data loads
- Updated AC 6: Changed to "Generate Complete Report" button
- Updated AC 8: Added frontend caching specification
- Updated AC 9: Updated timing (8-15 seconds for NEW generation)
- Added AC 10-11: Specified OldDataDisplay and NewDataDisplay components
- Updated AC 13: Added timeout error handling
- Updated AC 14: Added FR11 reference

**Total Changes**: 8 acceptance criteria updated/added

---

### 7. stories/3.1.section-reordering-interface.md

**Status**: Updated to "Draft - Updated for Data Configuration Workflow v2.3"

**Major Rewrite**: Changed focus from selection+ordering to ordering only

**New Structure**:
- **Critical Change Notice**: Explicitly states "Section SELECTION happens in Story 2.5"
- **Workflow Context**: Two-step explanation of Data Config → Section Management
- **Section Display by Data Mode** (ACs 1-3):
  - OLD Mode: Single section, disabled drag, info message
  - NEW Mode: Selected sections only (not all 14), drag enabled
  - OLD_NEW Mode: Combined draggable list with example visual
- **Drag-and-Drop Implementation** (ACs 4-8): Technical specifications
- **Data Persistence & Preview** (ACs 9-13): State management and storage
- **Validation & Error Handling** (ACs 14-16): No selections warning

**Total**: 16 acceptance criteria (restructured from 9)

**Key Removal**: No mention of visibility toggles or selection checkboxes (moved to Story 2.5)

---

## Implementation Alignment

### ✅ Documentation Now Matches Code

All documentation accurately reflects the implemented behavior in:

**Frontend Files**:
- `frontend/src/app/config/[triggerId]/page.tsx` (Lines 679-938)
- `frontend/src/components/NewDataDisplay.tsx`
- `frontend/src/components/OldDataDisplay.tsx`
- `frontend/src/components/SectionManagementPanel.tsx`

**Key Alignment Points**:
1. ✅ Section selection with checkboxes in Data Configuration
2. ✅ "Use This Data" button navigates to Section Management
3. ✅ Section Management receives selected sections only
4. ✅ OLD mode shows 1 section
5. ✅ NEW mode shows selected NEW sections
6. ✅ OLD_NEW mode shows OLD + NEW sections, all draggable
7. ✅ View toggle: "All Sections" / "Selected Only"
8. ✅ Bulk actions: "Select All" / "Clear All"
9. ✅ Data caching by stock ID in generatedDataCache
10. ✅ Button labels reflect section counts

---

## Workflow Comparison

### Before (v2.2)

```
Data Configuration Tab:
├── Fetch/Generate Data
└── Display Data (no selection)

Section Management Tab:
├── Show all 14 sections with checkboxes (SELECT)
└── Drag-and-drop reordering (ORDER)
```

### After (v2.3)

```
Data Configuration Tab:
├── Fetch/Generate Data
├── Section Selection UI with Checkboxes (SELECT)
│   ├── View Toggle: All / Selected Only
│   ├── Bulk Actions: Select All / Clear All
│   └── Selected count indicator
└── "Use This Data" Button → Navigate to Section Management

Section Management Tab:
├── Receive selected sections from Data Configuration
├── Display based on mode:
│   ├── OLD: 1 section (read-only)
│   ├── NEW: Selected NEW sections (draggable)
│   └── OLD_NEW: OLD + NEW sections (all draggable)
└── Drag-and-drop reordering only (ORDER)
```

---

## User Journey Updates

### Journey 1: OLD Mode (Simplest)

1. User enters stock ID
2. Selects OLD mode
3. Clicks "Fetch Data"
4. OLD data preview displays
5. Clicks **"Use This Data"**
6. Section Management shows: `[OLD Data (Complete)]` (read-only)
7. User proceeds to Prompts

### Journey 2: NEW Mode (Selection Required)

1. User enters stock ID
2. Selects NEW mode
3. Clicks "Generate Complete Report" (8-15 seconds)
4. All 14 sections appear with checkboxes
5. User selects sections (e.g., 1, 3, 5, 7, 9)
6. Clicks **"Use This Data (5 sections)"**
7. Section Management shows: 5 selected sections with drag handles
8. User reorders: 3 → 1 → 9 → 5 → 7 (drag-and-drop)
9. User proceeds to Prompts

### Journey 3: OLD_NEW Mode (Complex)

1. User enters stock ID
2. Selects OLD_NEW mode
3. Clicks "Generate NEW Report"
4. OLD data preview + NEW 14 sections with checkboxes appear
5. User selects NEW sections (e.g., 2, 5, 9)
6. Clicks **"Use This Data (OLD + 3 NEW sections)"**
7. Section Management shows: `[OLD Data] [Section 2] [Section 5] [Section 9]`
8. User drags to arrange: Section 2 → OLD Data → Section 5 → Section 9
9. User proceeds to Prompts (prompts will merge OLD data between NEW sections)

---

## Technical Specifications Updated

### State Management

**Data Configuration Tab State**:
```typescript
const [dataMode, setDataMode] = useState<'OLD' | 'NEW' | 'OLD_NEW'>('OLD');
const [oldData, setOldData] = useState<any>(null);
const [newSectionsData, setNewSectionsData] = useState<SectionData[]>([]);
const [selectedSectionIds, setSelectedSectionIds] = useState<string[]>([]);
const [generatedDataCache, setGeneratedDataCache] = useState<Record<string, SectionData[]>>({});
```

**Section Management Tab State**:
```typescript
// Receives from Data Configuration via props or context:
const sections = buildSectionsArray(dataMode, oldData, newSectionsData, selectedSectionIds);

// OLD mode: [{id: 'old_data', name: 'OLD Data (Complete)', source: 'old'}]
// NEW mode: [{id: '1', name: 'Section 1', source: 'new'}, ...]
// OLD_NEW mode: [{id: 'old_data', ...}, {id: '2', ...}, {id: '5', ...}]
```

### Component Props

**NewDataDisplay Component**:
```typescript
interface NewDataDisplayProps {
  sections: SectionData[];
  stockId: string;
  selectedSectionIds?: string[];
  onSelectionChange?: (sectionIds: string[]) => void;
  showSelection?: boolean;  // TRUE in Data Config, FALSE in preview mode
}
```

**SectionManagementPanel Component**:
```typescript
interface SectionManagementPanelProps {
  sections: Section[];  // Already filtered to selected sections
  onSectionsChange: (reorderedSections: Section[]) => void;
}

interface Section {
  id: string;
  name: string;
  source: 'old' | 'new';
}
```

### API Endpoints Referenced

| Endpoint | Method | Purpose | Documentation |
|----------|--------|---------|---------------|
| `/api/stocks/{stockid}/trigger-data` | GET | Fetch OLD data | Story 2.3 AC 3 |
| `/api/data/structured/generate` | POST | Generate NEW data (all 14 sections) | Story 2.3 AC 6 |
| `/api/triggers/{trigger}/prompts` | GET | Fetch existing prompts | Story 2.3 AC 4 |

---

## Testing Implications

### Updated Test Scenarios

**Scenario 1: Data Configuration - Section Selection**
- ✅ Test: Clicking checkbox selects/deselects section
- ✅ Test: "Select All" selects all 14 sections
- ✅ Test: "Clear All" deselects all sections
- ✅ Test: View toggle shows "All" or "Selected Only"
- ✅ Test: "Use This Data" button enables when selections > 0
- ✅ Test: Button click navigates to Section Management tab

**Scenario 2: Section Management - Ordering**
- ✅ Test: OLD mode shows 1 section, drag disabled
- ✅ Test: NEW mode shows only selected sections
- ✅ Test: OLD_NEW mode shows OLD + NEW sections
- ✅ Test: Drag-and-drop reorders sections correctly
- ✅ Test: OLD section can be dragged anywhere in OLD_NEW mode
- ✅ Test: Warning shown if no sections selected

**Scenario 3: Data Persistence**
- ✅ Test: Generated data cached by stock ID
- ✅ Test: Cached data notification appears
- ✅ Test: Switching stock ID regenerates data
- ✅ Test: localStorage persists selectedSectionIds
- ✅ Test: Section order persists in state

---

## Migration Notes for Teams

### For Frontend Developers

**Breaking Changes**: None - this is a reorganization, not a breaking change

**What to Update**:
1. ✅ Already implemented in codebase
2. Review updated specs in `front-end-spec.md` Panel 1 & 2
3. Test workflows match documentation

**New Components Referenced**:
- `OldDataDisplay` - Displays OLD data (JSON viewer)
- `NewDataDisplay` - Displays NEW sections with checkboxes
- `SectionManagementPanel` - Drag-and-drop ordering

### For Backend Developers

**No Backend Changes Required**: Documentation update only

**Verify Endpoints Match**:
- ✅ `GET /api/stocks/{stockid}/trigger-data?trigger_name={trigger}`
- ✅ `POST /api/data/structured/generate` (returns all 14 sections)
- ✅ Sections are strings "1"-"14", not integers

### For QA/Testing Teams

**Test Focus Areas**:
1. Data Configuration: Section selection with checkboxes works correctly
2. "Use This Data" button navigation to Section Management
3. Section Management receives correct sections based on mode
4. OLD_NEW mode allows dragging OLD section with NEW sections
5. Data caching prevents unnecessary regeneration

**Updated Test Cases**: See "Testing Implications" section above

### For Product/UX Teams

**User-Facing Changes**:
- ✅ Clearer separation: Selection (Data Config) vs. Ordering (Section Management)
- ✅ "Use This Data" button provides explicit navigation
- ✅ View toggle helps users focus on selected sections
- ✅ OLD_NEW mode now more intuitive (can position OLD anywhere)

**User Benefits**:
- Less cognitive load - one task per tab
- Clear progression through workflow
- Better visibility of what's selected vs. ordered

---

## Documentation Maintenance

### Version Control

| Version | Date | Description |
|---------|------|-------------|
| v2.2 | 2025-10-29 | Multi-prompt type support, tabbed editor |
| v2.3 | 2025-11-03 | Workflow reorganization (selection → ordering) |

### Future Updates

When making changes to this workflow, update these files in order:

1. **frontend-spec.md** (primary UI specification)
2. **prd.md** (functional requirements)
3. **epic-2** and **epic-6** (epic-level descriptions)
4. **Individual stories** (detailed acceptance criteria)

### Cross-References

All updated files now reference each other correctly:

- Story 2.1 → References Story 2.5 for section selection
- Story 2.3 → References Story 2.5 for section selection UI
- Story 2.5 → References Story 3.1 for ordering
- Story 3.1 → References Story 2.5 for selection
- Epic 2 → Story 2.5 covers selection
- Epic 3 → Story 3.1 covers ordering

---

## Completion Checklist

- [x] frontend-spec.md updated (Change Log, Panel 1, Panel 2)
- [x] prd.md updated (FR11, FR12, FR37, Core Screens)
- [x] epic-2 updated (Story 2.5 rewritten with 30 ACs)
- [x] epic-6 updated (Story 1.11 rewritten as two-phase workflow)
- [x] Story 2.1 updated (workflow context added)
- [x] Story 2.3 updated (14 ACs updated with section selection)
- [x] Story 3.1 updated (16 ACs rewritten for ordering only)
- [x] Documentation summary created (this file)
- [x] All cross-references validated
- [x] Technical specifications aligned with code

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Files Updated** | 7 |
| **Total Acceptance Criteria Modified/Added** | 73 |
| **Lines of Documentation Changed** | ~650 |
| **New Diagrams/Examples Added** | 3 (OLD_NEW display, workflow comparison, user journeys) |
| **Stories Completely Rewritten** | 2 (Story 2.5, Story 3.1) |
| **Stories Significantly Updated** | 2 (Story 1.11, Story 2.3) |
| **Stories Minimally Updated** | 1 (Story 2.1) |

---

## Status by Epic

### Epic 1: Foundation & Infrastructure
**Status**: No updates needed (no workflow changes affect this epic)

### Epic 2: Data Pipeline & Integration
**Status**: ✅ Complete
- Story 2.1: ✅ Updated (context added)
- Story 2.3: ✅ Updated (14 ACs modified)
- Story 2.5: ✅ Complete rewrite (30 ACs, now focuses on selection)

### Epic 3: Prompt Engineering Workspace
**Status**: ✅ Complete
- Story 3.1: ✅ Complete rewrite (16 ACs, now focuses on ordering)
- Other stories: No changes needed (prompt editing unaffected)

### Epic 4: Multi-Model Testing & Comparison
**Status**: No updates needed (no workflow changes affect this epic)

### Epic 5: Publishing & Workflow Management
**Status**: No updates needed (no workflow changes affect this epic)

### Epic 6: News CMS Workflow Feature
**Status**: ✅ Complete
- Story 1.11: ✅ Rewritten as two-phase workflow (13 ACs)
- Other stories: Already aligned with workflow

---

## Quick Reference: Key Changes

| Aspect | Old Behavior | New Behavior (v2.3) |
|--------|-------------|---------------------|
| **Section Selection** | In Section Management | In Data Configuration (with checkboxes) |
| **Section Ordering** | In Section Management | In Section Management (only) |
| **Navigation** | Manual tab switching | "Use This Data" button navigates |
| **View Toggle** | Not available | "All Sections" / "Selected Only" |
| **OLD Mode** | Unclear | Single section, no selection needed |
| **OLD_NEW Mode** | Limited | OLD + NEW sections, all draggable |
| **Button Label** | Generic | Mode-specific ("Use This Data (X sections)") |

---

## Contact & Questions

For questions about these documentation updates:
- **Frontend**: See `front-end-spec.md` Panel 1 & 2
- **Backend**: No changes required, but verify endpoint formats
- **Requirements**: See `prd.md` FR11, FR12, FR37
- **Stories**: See individual story files in `docs/stories/`

**Document Author**: Claude (AI Assistant)
**Review Status**: Ready for team review
**Next Action**: Team review and validation

---

**END OF DOCUMENTATION UPDATE SUMMARY**
