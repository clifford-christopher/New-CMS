# Figma AI Complete Prompts - News CMS UI Design (v2.2)

**Document Purpose:** Complete, ready-to-use Figma AI prompts for creating the entire News CMS UI/UX with dropdown-based trigger selection.

**Key Changes from v2.1:**
- **Backend Default Selections:** Data sections pre-selected by backend on page load
- **Button Renamed:** "Fetch Data" → "Use This Data" with clearer workflow
- **Status Badge Added:** "Default configuration" indicator for initial state
- **Trigger Context Bar Updated:** Removed redundant Fetch Data button, replaced with status badge
- **Section Management Updated:** Dynamically shows only selected sections from Data Configuration

**Key Changes from v2.0:**
- **Prompt #6 Updated:** Data Configuration redesigned with multi-select dropdown + checkboxes for 14 hardcoded data sections
- Removed "Add API" pattern in favor of section-based selection
- Enhanced UX with "Select All" / "Clear All" functionality
- Improved data fetching workflow with validation

**Key Changes from v1.0:**
- Dashboard redesigned with dropdown trigger selector (no card grid)
- Streamlined workflow-focused layout
- MVP scope: Removed Audit Log and Settings screens
- Focus on core configuration workflow only
- Copy-paste ready prompts with exact specifications

---

## Setup Instructions

### Before You Begin

1. **Create New Figma File:**
   - File name: "News CMS UI Design"
   - Canvas size: 1920x1080px (desktop primary viewport)
   - Set up 2 pages: "Screens" and "Components"

2. **Install Fonts** (if not already available):
   - System fonts will be used (San Francisco, Segoe UI, Roboto)
   - Monospace: SF Mono, Consolas, Monaco

3. **Color Palette Setup:**
   Create color styles in Figma before starting:
   - Primary Blue: `#0d6efd`
   - Secondary Gray: `#6c757d`
   - Success Green: `#198754`
   - Warning Yellow: `#ffc107`
   - Danger Red: `#dc3545`
   - Info Cyan: `#0dcaf0`
   - Light Gray: `#f8f9fa`
   - Dark: `#212529`
   - Border Gray: `#dee2e6`

4. **Bootstrap 5 Reference:**
   Keep Bootstrap 5 documentation open for component reference: https://getbootstrap.com/docs/5.0/

---

## PHASE 1: FOUNDATION & NAVIGATION

### Prompt #1: Top Navigation Bar (Navbar)

Create a top navigation bar (Bootstrap navbar style) for the News CMS application.

**Navbar Container:**
- Width: 1920px (full viewport width)
- Height: 64px
- Background: Dark (#212529)
- Position: Sticky top
- Shadow: 0 2px 4px rgba(0,0,0,0.1)

**Left Section (Brand Area):**
- Logo/Brand area: 200px width
- Text: "News CMS" (or placeholder for logo image)
- Font: 24px, semi-bold, white (#ffffff)
- Padding-left: 24px from edge

**Center Section (Navigation Links):**
Horizontal nav links:
1. "Dashboard" - Active state (underline: 2px solid #0d6efd, text: white)
2. "Configuration Workspace" - Inactive state (text: #adb5bd, hover: white) - Only shown when trigger selected

Each link:
- Font: 16px, medium weight
- Padding: 20px horizontal
- Transition: 200ms ease

**Right Section (User Area):**
- User icon (circle, 32px diameter, background #6c757d)
- User name: "Admin User" (14px, #adb5bd)
- Padding-right: 24px from edge

**After AI Generates:**
1. Convert to component and name "Navbar/Primary"
2. Create variant for active states (Dashboard, Configuration Workspace)
3. Ensure shadow is visible on white background
4. Note: Configuration Workspace link is context-dependent (only visible when trigger selected)

---

### Prompt #2: Breadcrumb Navigation

Create a breadcrumb navigation component (Bootstrap breadcrumb style).

**Breadcrumb Container:**
- Height: 40px
- Background: White (#ffffff)
- Border-bottom: 1px solid #dee2e6
- Padding: 8px 24px

**Breadcrumb Items:**
Display pattern: "Dashboard > [Trigger Name] > [Current Panel]"

Example: "Dashboard > Earnings Alert > Prompt Engineering"

**Item Styling:**
- Font: 14px, regular weight
- Clickable items (Dashboard, Trigger Name): Color #0d6efd, underline on hover
- Current item (last): Color #6c757d, no underline, not clickable
- Separator: ">" character, color #adb5bd, 8px margin left/right

**States:**
- Default: 2 items ("Dashboard > Current View")
- Expanded: 3 items (when in Configuration Workspace)

**After AI Generates:**
1. Create component variants for 2-item and 3-item versions
2. Name component "Breadcrumb/Navigation"
3. Ensure text is selectable for accessibility

---

## PHASE 2: DASHBOARD SCREEN (REDESIGNED)

### Prompt #3: Dashboard Main Layout - Dropdown Trigger Selector

Create the main dashboard screen with a workflow-focused layout using a dropdown trigger selector.

**Canvas Size:** 1920x1080px

**TOP SECTION - Navigation:**
- Include Navbar component (from Prompt #1) at top
- Include Breadcrumb showing "Dashboard" (from Prompt #2) below navbar

**MAIN CONTENT AREA:**
Background: Light gray (#f8f9fa)
Padding: 40px (top, left, right), extends to bottom of viewport

**Page Header Section:**
- Container: Full width (1856px after padding)
- Margin-bottom: 32px

**Title:** "News Trigger Dashboard"
- Font: 32px (H2), semi-bold, dark (#212529)
- Margin-bottom: 8px

**Subtitle:** "Configure and manage AI-powered news generation triggers"
- Font: 16px, regular, secondary gray (#6c757d)

**TRIGGER SELECTOR SECTION:**
Create a prominent centered selector area:

**Container:**
- Width: 600px
- Center aligned (horizontally on page)
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 32px
- Shadow: 0 2px 8px rgba(0,0,0,0.1)

**Label:** "Select Trigger to Configure"
- Font: 18px, medium weight, dark (#212529)
- Margin-bottom: 16px

**Dropdown Field:**
- Width: 100% (536px after padding)
- Height: 48px
- Border: 1px solid #ced4da
- Border-radius: 4px
- Padding: 12px 16px
- Font: 16px, regular

**Placeholder text:** "Choose a trigger..."

**Dropdown Content** (shown when opened):
List of trigger options with status indicators:
1. "Earnings Alert" - Badge: "Configured" (green #198754)
2. "Analyst Grade Change" - Badge: "Configured" (green #198754)
3. "Price Target Update" - Badge: "Unconfigured" (gray #6c757d)
4. "Market Commentary" - Badge: "In Progress" (yellow #ffc107)
5. "Dividend Announcement" - Badge: "Unconfigured" (gray #6c757d)

Each dropdown item:
- Height: 56px
- Padding: 12px 16px
- Hover: Background #f8f9fa
- Layout: Trigger name (left, 16px font) + Status badge (right, 12px font, padding 4px 8px, border-radius 12px)

**Action Button:**
Below dropdown, 16px margin-top:
- Button: "Configure Selected Trigger"
- Style: Primary blue (#0d6efd), white text
- Width: 100%
- Height: 48px
- Border-radius: 4px
- Font: 16px, medium weight
- Disabled state (if no selection): Background #e9ecef, text #6c757d, cursor not-allowed

**QUICK STATS SECTION** (below selector):
Margin-top: 48px from selector

**Container:**
- Width: 1200px
- Center aligned
- Display: 3 columns (equal width, 16px gap)

Create 3 stat cards:

**Card 1 - Total Triggers:**
- Background: White
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 1px 3px rgba(0,0,0,0.08)

Icon: Circle with number "5" (48px diameter, background #e7f1ff, text #0d6efd, 24px font)
Label: "Total Triggers" (14px, #6c757d, margin-top 12px)
Value: "5" (32px, bold, #212529, margin-top 4px)

**Card 2 - Configured:**
Same layout as Card 1
Icon: Checkmark in circle (48px, background #d1f4e0, text #198754)
Label: "Configured"
Value: "2"

**Card 3 - Recent Activity:**
Same layout as Card 1
Icon: Clock in circle (48px, background #fff3cd, text #ffc107)
Label: "Last Updated"
Value: "2 hours ago" (20px font)

**RECENT ACTIVITY SECTION** (below stats):
Margin-top: 32px

**Heading:** "Recent Configuration Changes"
- Font: 20px, medium weight
- Margin-bottom: 16px

**Activity List:**
- Width: 1200px, center aligned
- Background: White
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 1px 3px rgba(0,0,0,0.08)

List of 5 recent activity items (table-like layout):
Each row:
- Height: 48px
- Border-bottom: 1px solid #f8f9fa (except last)
- 4 columns: Timestamp | Trigger Name | User | Action

Example row 1:
- "2 hours ago" (14px, #6c757d)
- "Earnings Alert" (14px, #212529)
- "John Doe" (14px, #6c757d)
- "Published v1.3" (14px, badge style, success green)

**After AI Generates:**
1. Ensure dropdown has both closed and opened states
2. Create component for stat cards (reusable)
3. Verify centered alignment of main sections
4. Ensure disabled button state is clearly visible

---

## PHASE 3: CONFIGURATION WORKSPACE - LAYOUT & STRUCTURE

### Prompt #4: Configuration Workspace - Main Layout & Sidebar

Create the Configuration Workspace main layout with left sidebar navigation.

**Canvas Size:** 1920x1080px

**TOP SECTION:**
- Include Navbar component (sticky)
- Include Breadcrumb: "Dashboard > Earnings Alert > Data Configuration"

**LAYOUT STRUCTURE:**

**Left Sidebar (Fixed):**
- Width: 280px
- Height: 100% (from below breadcrumb to bottom)
- Background: White (#ffffff)
- Border-right: 1px solid #dee2e6
- Padding: 24px 16px

**Sidebar Header:**
- Text: "Configuration Steps"
- Font: 14px, uppercase, semi-bold, #6c757d
- Margin-bottom: 24px

**Sidebar Navigation Items** (vertical list, 16px gap between items):

Create 5 navigation items (accordion/list style):

**Item 1: Data Configuration**
- Active state (currently selected)
- Background: Light blue (#e7f1ff)
- Border-left: 3px solid #0d6efd
- Padding: 12px 16px
- Border-radius: 4px (right side only)

Layout:
- Icon: Database icon (16px, #0d6efd, left)
- Text: "Data Configuration" (14px, medium, #0d6efd)
- Status: Checkmark icon (16px, #198754, right) - indicates completion

**Item 2: Section Management**
- Inactive state
- Background: Transparent
- Padding: 12px 16px

Layout:
- Icon: List icon (16px, #6c757d)
- Text: "Section Management" (14px, regular, #212529)
- Status: Checkmark icon (16px, #198754, right)

**Item 3: Prompt Engineering**
- Inactive state (same styling as Item 2)
- Icon: Code icon
- Text: "Prompt Engineering"
- Status: Checkmark icon (greyed out #dee2e6) - not completed

**Item 4: Model Testing**
- Inactive state
- Icon: Beaker/test icon
- Text: "Model Testing"
- Status: No checkmark (not completed)

**Item 5: Results & Comparison**
- Inactive state
- Icon: Split-pane icon
- Text: "Results & Comparison"
- Status: No checkmark (not completed)

**Main Content Area:**
- Position: To right of sidebar
- Width: 1640px (1920 - 280 sidebar)
- Background: Light gray (#f8f9fa)
- Padding: 32px
- Height: 100% (scrollable)

**Content Header:**
- Text: "Data Configuration"
- Font: 28px, semi-bold, dark (#212529)
- Margin-bottom: 24px

**Placeholder Content:**
- Text: "[Content panels will be placed here]"
- Font: 16px, italic, #6c757d
- Background: White, padding 24px, border-radius 8px

**Bottom Actions Bar (Sticky):**
- Position: Fixed bottom
- Width: 1640px (matches main content area width)
- Height: 72px
- Background: White (#ffffff)
- Border-top: 1px solid #dee2e6
- Padding: 16px 32px
- Shadow: 0 -2px 8px rgba(0,0,0,0.05)

**Actions Bar Content:**
Left side:
- "Save Draft" button (secondary, gray outline, 120px width, 40px height)
- "View History" button (secondary, gray outline, 120px width, 16px margin-left)

Right side:
- "Publish" button (primary blue, 140px width, 40px height, semi-bold)
- Disabled state (background #e9ecef, text #6c757d)
- Tooltip on hover: "Complete all required steps before publishing"

**After AI Generates:**
1. Create component for sidebar navigation item (with active/inactive variants)
2. Ensure bottom actions bar spans full content area width
3. Create variant for each navigation item as active state
4. Verify scrollable content area

---

### Prompt #5: Trigger Context Bar with Type Selection

Create a trigger context bar with prompt type selection that sits at the top of the Configuration Workspace content area.

**Container:**
- Width: 1576px (full content width minus padding)
- Height: 140px (increased for type selection row)
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 20px 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Layout:** Vertical flex layout

**TOP ROW - Trigger Info & Stock ID:**
Horizontal flex layout, space-between alignment

**Left Section - Trigger Info:**
- Trigger name: "Earnings Alert" (20px, semi-bold, #212529)
- Last updated: "Last published: 2 days ago (v1.2)" (14px, #6c757d, 4px margin-top)

**Center Section - Stock ID Input:**
Label: "Test Stock ID" (12px, #6c757d, above input)
Input field:
- Width: 200px
- Height: 40px
- Border: 1px solid #ced4da
- Border-radius: 4px
- Padding: 8px 12px
- Placeholder: "Enter stock ID (e.g., TCS)"
- Font: 14px
- Default value: Pre-populated with stock ID if available

**Input Behavior:**
- On blur (when user leaves field after editing): Automatically triggers data fetch for all selected sections with new stock ID
- Debounced: Wait 500ms after user stops typing before triggering fetch
- Shows loading indicator during fetch
- Updates all data sections with new stock-specific data

**Right Section - Configuration Status:**
Status badge showing data configuration state:

**State 1: Not Configured** (initial)
- Badge: "Configure Data" (14px, secondary gray #6c757d background, white text, padding 6px 12px, border-radius 12px)

**State 2: Data Fetched** (after clicking "Use This Data" or changing Stock ID)
- Badge: "Data Ready" (14px, success green #198754 background, white text, padding 6px 12px, border-radius 12px)
- Icon: Checkmark (12px, white, left of text)
- Subtext: "for TCS" (12px, #6c757d, 4px margin-left) - shows current stock ID

**State 3: Fetching Data** (during Stock ID change or initial fetch)
- Badge: "Fetching Data..." (14px, info cyan #0dcaf0 background, white text, padding 6px 12px, border-radius 12px)
- Icon: Spinner (12px, white, animated rotation, left of text)

**State 4: Error**
- Badge: "Configuration Error" (14px, danger red #dc3545 background, white text, padding 6px 12px, border-radius 12px)
- Icon: Warning triangle (12px, white, left of text)

---

**BOTTOM ROW - Prompt Type Selection** (16px margin-top from top row):
- Divider: 1px solid #dee2e6 (full width, 12px margin-bottom)
- Label: "Prompt Types" (14px, medium, #6c757d, 8px margin-bottom)
- Layout: Horizontal flex, 24px gap between checkboxes

**Type Selection Checkboxes:**

**Checkbox 1: Paid** (always checked, disabled)
- Checkbox: 20px square, checked state (blue #0d6efd with white checkmark)
- Icon: 💰 (16px, left of text, 8px margin-right)
- Text: "Paid" (14px, semi-bold, #212529, 8px margin-left from checkbox)
- Badge: "Default" (12px, light blue background #e7f1ff, text #0d6efd, padding 2px 6px, border-radius 8px, 8px margin-left)
- Disabled state (cannot be unchecked)

**Checkbox 2: Unpaid** (optional, unchecked by default)
- Checkbox: 20px square, unchecked state (border #ced4da)
- Icon: 🆓 (16px, left of text, 8px margin-right)
- Text: "Unpaid" (14px, regular, #212529, 8px margin-left from checkbox)
- Clickable (can be checked/unchecked)

**Checkbox 3: Web Crawler** (optional, unchecked by default)
- Checkbox: 20px square, unchecked state (border #ced4da)
- Icon: 🕷️ (16px, left of text, 8px margin-right)
- Text: "Web Crawler" (14px, regular, #212529, 8px margin-left from checkbox)
- Clickable (can be checked/unchecked)

**Helper Text** (below checkboxes, 8px margin-top):
- Text: "Select the prompt types to configure and test. Paid is always included." (12px, italic, #6c757d)

---

**After AI Generates:**
1. Create component "TriggerContextBar" with two-row layout
2. Create **four badge variants** for status (top right):
   - "Configure Data" (gray) - initial
   - "Fetching Data..." (cyan with spinner) - loading
   - "Data Ready for [STOCK]" (green with checkmark) - success
   - "Configuration Error" (red with warning) - error
3. Create checkbox component with three states:
   - Checked and disabled (Paid - blue with checkmark, grayed cursor)
   - Checked and enabled (blue with checkmark)
   - Unchecked (border only)
4. Ensure input field has focus state (blue border)
5. Stock ID should be pre-populated from backend if available
6. **Implement auto-fetch behavior**: When Stock ID changes (on blur or after 500ms debounce), automatically fetch data for all selected sections
7. Position at top of content area in workspace layout
8. Badge updates automatically based on data configuration state
9. Show loading spinner in badge during fetch triggered by Stock ID change
10. Checkbox selection controls which prompt tabs are shown in the Prompt Editor (Prompt #10)
11. Icon + text + badge alignment should be consistent across all three checkbox options

---

## PHASE 4: DATA CONFIGURATION PANELS

### Prompt #6: Data Section Selection Panel (Multi-Select Dropdown with Checkboxes)

Create a data section selection panel with a multi-select dropdown containing checkboxes for 14 hardcoded data sections. The backend provides default selections that users can modify.

**Panel Container:**
- Width: 1576px (fills content area with padding)
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Panel Header:**
- Text: "Data Configuration"
- Font: 20px, semi-bold, dark (#212529)
- Margin-bottom: 16px

**Description:**
- Text: "Default data sections are pre-selected based on this trigger's configuration. Modify your selection if needed, then fetch data. Data will be fetched for the stock ID specified above."
- Font: 14px, regular, #6c757d
- Margin-bottom: 24px

**Info Callout** (if no stock ID entered):
- Background: Light yellow (#fff3cd)
- Border-left: 3px solid #ffc107
- Padding: 12px 16px
- Border-radius: 4px
- Margin-bottom: 16px
- Icon: Info circle (16px, #ffc107, left)
- Text: "Enter a Stock ID above to fetch data for testing" (14px, #212529, 12px margin-left from icon)

**Section Selection Dropdown:**

**Label:**
- Text: "Select Data Sections to Include"
- Font: 14px, medium, #212529
- Margin-bottom: 8px

**Dropdown Button** (closed state - DEFAULT WITH SELECTIONS):
- Width: 100% (full width)
- Height: 48px
- Border: 1px solid #ced4da
- Border-radius: 4px
- Background: White (#ffffff)
- Padding: 12px 16px
- Font: 16px, regular

Layout (horizontal, space-between):
- LEFT:
  - **Default State**: "5 sections selected" (medium weight, #0d6efd) - Shows pre-selected count from backend
  - If user clears all: "Choose sections..." (gray, #6c757d)
- RIGHT:
  - Chevron-down icon (16px, #6c757d, rotates when dropdown opens)

**Visual Indicator** (below button, 4px margin-top):
- Small badge: "Default configuration" (12px, light blue background #e7f1ff, text #0d6efd, padding 2px 6px, border-radius 4px)
- Only shown on initial load before user modifies selections

**Dropdown Menu** (opened state):
- Width: 100% (matches button width)
- Max-height: 400px (scrollable if content exceeds)
- Border: 1px solid #ced4da
- Border-radius: 4px
- Background: White (#ffffff)
- Shadow: 0 4px 12px rgba(0,0,0,0.15)
- Position: Below dropdown button (8px gap)
- Padding: 8px 0
- Z-index: High (above other content)

**Dropdown Items** (14 sections with checkboxes):

Create 14 checkbox items in a vertical list. **Show default selections on initial load:**

**Item 1:** ✓ CHECKED (default from backend)
- Height: 48px
- Padding: 12px 16px
- Hover background: #f8f9fa
- Cursor: pointer
- Border-bottom: 1px solid #f8f9fa (except last item)

Layout (horizontal, aligned center):
- LEFT:
  - Checkbox: 20px square, **CHECKED** - blue (#0d6efd) with white checkmark
  - Section name: "Section 1: Company Information" (14px, regular, #212529, 12px margin-left)
- Full item is clickable (not just checkbox)

**Item 2:** ✓ CHECKED (default)
Same layout
- Checkbox: **CHECKED**
- Text: "Section 2: Quarterly Income Statement"

**Item 3:** ✓ CHECKED (default)
- Checkbox: **CHECKED**
- Text: "Section 3: Annual Income Statement"

**Item 4:** UNCHECKED
- Checkbox: **UNCHECKED** - border #ced4da
- Text: "Section 4: Balance Sheet"

**Item 5:** ✓ CHECKED (default)
- Checkbox: **CHECKED**
- Text: "Section 5: Cash Flow Statement"

**Item 6:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 6: Key Financial Ratios & Metrics"

**Item 7:** ✓ CHECKED (default)
- Checkbox: **CHECKED**
- Text: "Section 7: Valuation Metrics"

**Item 8:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 8: Shareholding Pattern"

**Item 9:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 9: Stock Price & Returns Analysis"

**Item 10:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 10: Technical Analysis"

**Item 11:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 11: Quality Assessment"

**Item 12:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 12: Financial Trend Analysis"

**Item 13:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 13: Proprietary Score & Advisory"

**Item 14:** UNCHECKED
- Checkbox: **UNCHECKED**
- Text: "Section 14: Peer Comparison"

**Note for Designer:** Show 5 sections checked by default (Items 1, 2, 3, 5, 7) to represent backend default configuration. This should be adjustable in your design system.

**Dropdown Footer** (sticky bottom inside dropdown):
- Background: Light gray (#f8f9fa)
- Border-top: 1px solid #dee2e6
- Padding: 12px 16px
- Height: 56px

Layout (horizontal, space-between):
- LEFT:
  - "Clear All" link (14px, #0d6efd, underline on hover, clickable)
- RIGHT:
  - "Select All" link (14px, #0d6efd, underline on hover)

**Use This Data Button** (below dropdown, 16px margin-top):
- Button: "Use This Data"
- Style: Primary blue (#0d6efd), white text
- Width: 200px
- Height: 48px
- Border-radius: 4px
- Icon: Arrow-right icon (16px, right of text, 8px margin-left)
- Font: 16px, medium weight

**Button States:**

**Default/Enabled State** (with selections):
- Primary blue background
- Enabled on page load (since backend provides default selections)
- Tooltip: "Fetch data for selected sections and proceed to section management"

**Disabled State** (if user clears all selections):
- Background: #e9ecef
- Text: #6c757d
- Cursor: not-allowed
- Border: 1px solid #dee2e6
- Tooltip on hover: "Please select at least one data section"

**Loading State** (during data fetch):
- Background: Primary blue (slightly darker #0b5ed7)
- Spinner icon replacing arrow icon
- Text: "Fetching data..."
- Disabled (non-clickable)

**Helper Text** (below button, 8px margin-top):
- Text: "This will fetch data for 5 selected sections" (12px, #6c757d)
- Updates dynamically based on selection count

**After AI Generates:**
1. **Create initial state with default selections**: Show 5 checkboxes pre-checked (Items 1, 2, 3, 5, 7) and button enabled
2. Create both dropdown states: closed (button showing "5 sections selected") and opened (with menu)
3. Create checkbox component with checked/unchecked states
4. Show "Default configuration" badge on initial load; remove when user modifies selections
5. Show selected count updating dynamically in dropdown button text (e.g., "7 sections selected")
6. Ensure dropdown menu has proper shadow and positioning
7. Add hover states for all checkbox items (light gray background)
8. **Create three button states**: Default (enabled), Disabled (no selections), Loading (fetching data)
9. Update helper text dynamically based on selection count
10. Ensure entire checkbox item row is clickable (not just the checkbox itself)
11. Add smooth dropdown open/close animation
12. Dropdown should close when clicking outside or pressing Escape key
13. Dropdown remains open while selecting/deselecting items
14. **Workflow**: Clicking "Use This Data" fetches data and advances to Section Management panel

---

### Prompt #7: Raw JSON Display Panel

Create a collapsible panel displaying raw JSON responses from APIs.

**Panel Container:**
- Width: 1576px
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Panel Header** (collapsible):
- Icon: Chevron-down (16px, #6c757d, rotates when collapsed)
- Text: "Raw JSON Response"
- Font: 20px, semi-bold, dark (#212529)
- "Collapse/Expand" interaction (entire header clickable)
- Border-bottom: 1px solid #dee2e6
- Padding-bottom: 16px
- Margin-bottom: 16px

**Content Section** (expanded state):

Create 3 JSON code blocks (one per API):

**JSON Block 1 - Earnings API:**
- Label: "Earnings API Response" (14px, medium, #212529, margin-bottom 8px)
- Container: Dark background (#2d2d2d), border-radius 4px, padding 16px
- Max-height: 300px, scrollable (vertical scroll if content exceeds)

JSON content (syntax-highlighted):
```json
{
  "symbol": "AAPL",
  "quarter": "Q4 2024",
  "revenue": "119.58B",
  "eps": "2.18",
  "earnings_date": "2024-10-31",
  "summary": "Apple reported strong Q4 results..."
}
```

**Text styling:**
- Font: Monospace (SF Mono, Consolas), 14px, line height 20px
- Property names (keys): Light blue (#9cdcfe)
- String values: Orange (#ce9178)
- Number values: Light green (#b5cea8)
- Brackets/punctuation: Light gray (#d4d4d4)

**Copy Button:**
- Position: Top-right corner of JSON block
- Button: "Copy" (secondary, small, 60px width, 28px height)
- Icon: Clipboard icon (14px)
- Click state: Changes to "Copied!" with checkmark icon

**JSON Block 2 - Sentiment Analysis API:**
Same layout as Block 1
- Different mock JSON data

**JSON Block 3 - Historical Prices API:**
Same layout
- Show error state: Red border around container, error icon, message "Failed to load"

**After AI Generates:**
1. Create collapsed state variant (header only, content hidden)
2. Add smooth expand/collapse animation indicator
3. Ensure JSON text is selectable
4. Create copy button component with clicked state
5. Add horizontal scroll if JSON lines are too long

---

### Prompt #8: Structured Data Preview Panel

Create a panel showing parsed, structured data in a user-friendly format.

**Panel Container:**
- Width: 1576px
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Panel Header:**
- Text: "Structured Data Preview"
- Font: 20px, semi-bold, dark (#212529)
- Margin-bottom: 8px

**Subheading:**
- Text: "Parsed data available as placeholders in your prompt"
- Font: 14px, regular, #6c757d
- Margin-bottom: 24px

**Data Sections:**
Create 3 data section cards (16px gap between):

**Section 1 - Earnings Data:**

**Section Header:**
- Background: Light blue (#e7f1ff)
- Padding: 12px 16px
- Border-radius: 6px 6px 0 0
- Text: "Earnings Data" (16px, medium, #0d6efd)
- Placeholder tag: "{{earnings}}" (12px, mono font, orange #ce9178, right-aligned)

**Section Body:**
- Background: White
- Border: 1px solid #dee2e6
- Border-radius: 0 0 6px 6px
- Padding: 16px

Data table layout (2 columns: label + value):

Row 1:
- Label: "Symbol" (14px, #6c757d, 140px width)
- Value: "AAPL" (14px, semi-bold, #212529)

Row 2:
- Label: "Quarter"
- Value: "Q4 2024"

Row 3:
- Label: "Revenue"
- Value: "$119.58B" (success green #198754, semi-bold)

Row 4:
- Label: "EPS"
- Value: "$2.18"

Row 5:
- Label: "Earnings Date"
- Value: "October 31, 2024"

Row 6:
- Label: "Summary"
- Value: "Apple reported strong Q4 results with revenue beating expectations..." (multi-line, max-width, normal weight)

**Section 2 - Sentiment Analysis:**
Same layout as Section 1
- Header: "Sentiment Analysis" with placeholder "{{sentiment}}"
- Data rows:
  - Score: "0.78" (number with badge indicator)
  - Label: "Positive" (success green badge)
  - Confidence: "High (92%)"
  - Key phrases: "strong results, beat expectations, positive outlook"

**Section 3 - Historical Prices:**
Same layout
- Header: "Historical Prices" with placeholder "{{prices}}"
- Data rows:
  - Current: "$178.45"
  - 1-week change: "+$4.32 (2.48%)" (green with up arrow)
  - 1-month change: "+$12.15 (7.31%)" (green)
  - 52-week high: "$198.23"
  - 52-week low: "$164.08"

**After AI Generates:**
1. Ensure placeholder tags ({{variable}}) use monospace font and orange color
2. Create section component (reusable for different data types)
3. Verify table-like alignment of labels and values
4. Add subtle hover effect on sections

---

## PHASE 5: SECTION MANAGEMENT PANEL

### Prompt #9: Section Reordering Interface

Create a drag-and-drop section reordering panel. This panel receives the selected data sections from Prompt #6 and allows users to reorder them.

**Panel Container:**
- Width: 1576px
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Panel Header:**
- Text: "Section Management"
- Font: 20px, semi-bold, dark (#212529)
- Margin-bottom: 8px

**Description:**
- Text: "Reorder the sections below to control how data appears in your prompt. Only the 5 sections you selected are shown."
- Font: 14px, regular, #6c757d
- Margin-bottom: 24px

**Reorderable Section List:**
Create 5 draggable items (8px gap between) - **showing only the sections selected in Prompt #6**:

**Draggable Item 1:**
- Container: Light background (#f8f9fa)
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Padding: 16px
- Height: 64px
- Cursor: grab (indicates draggable)

Layout (horizontal, aligned center):
- LEFT SIDE:
  - Drag handle icon: 6 horizontal dots (2 rows of 3, gray #6c757d, 20px)
  - Number input: Width 60px, height 38px, border 1px solid #ced4da, value "1", centered text
  - Section name: "Company Information" (16px, medium, #212529, 16px margin-left)

- RIGHT SIDE:
  - Placeholder: "{{section_1}}" (14px, mono, orange #ce9178)

**Draggable Item 2:**
Same layout
- Number: "2"
- Name: "Quarterly Income Statement"
- Placeholder: "{{section_2}}"

**Draggable Item 3:**
Same layout
- Number: "3"
- Name: "Annual Income Statement"
- Placeholder: "{{section_3}}"

**Draggable Item 4:**
Same layout
- Number: "4"
- Name: "Cash Flow Statement"
- Placeholder: "{{section_5}}"

**Draggable Item 5:**
Same layout
- Number: "5"
- Name: "Valuation Metrics"
- Placeholder: "{{section_7}}"

**Note for Designer:** The list should dynamically display only the sections selected in Data Configuration (Prompt #6). In this example, 5 sections match the default selections (Items 1, 2, 3, 5, 7).

**Preview Button:**
Below list, 16px margin-top:
- Button: "Preview Data Structure"
- Style: Secondary outline (gray border, gray text)
- Width: 200px
- Height: 40px
- Icon: Eye icon (16px, left)

**After AI Generates:**
1. Add visual hover state for draggable items (cursor changes to grab)
2. Show "dragging" state variant (opacity 0.6, shadow increase)
3. Add number input focus state
4. Ensure drag handle icon is clearly visible
5. Create drop zone indicator (dashed border between items)

---

## PHASE 6: PROMPT ENGINEERING PANEL

### Prompt #10: Tabbed Monaco Editor Integration Panel

Create a Monaco Editor-style prompt editor panel with tabbed interface for multiple prompt types.

**Panel Container:**
- Width: 1576px (fills content area with padding)
- Background: White (#ffffff)
- Border-radius: 8px
- Shadow: 0 2px 8px rgba(0,0,0,0.1)
- Margin-bottom: 24px

**TOOLBAR WITH TABS** (top section):
- Width: 1576px (full panel width)
- Height: 96px (increased for tabs row)
- Background: Light gray (#f8f9fa)
- Border-bottom: 1px solid #dee2e6
- Border-radius: 8px 8px 0 0
- Padding: 12px 16px

**TOP ROW - Title & Actions:**
Horizontal layout, space-between

**Left Side:**
- Title: "Prompt Template" (16px, medium, #212529)
- Auto-save indicator: "Saved 2 minutes ago" (12px, #6c757d, italic, 12px margin-left)

**Right Side:**
Toolbar buttons (horizontal, 8px gap):
- "Undo" button (secondary, icon-only, 32px square)
- "Redo" button (secondary, icon-only, 32px square)
- Divider (vertical line, 24px height, #dee2e6)
- "Preview" button (secondary, 100px width, 32px height)
- "History" button (secondary, 100px width, 32px height)

---

**BOTTOM ROW - Prompt Type Tabs** (12px margin-top):
Horizontal tab navigation, 8px gap

**Tab 1: Paid** (active - always visible)
- Height: 40px, Padding: 10px 20px
- Background: White (#ffffff)
- Border-bottom: 3px solid #0d6efd
- Icon: 💰 (16px, 8px margin-right)
- Text: "Paid" (14px, semi-bold, #0d6efd)

**Tab 2: Unpaid** (inactive - only if checked)
- Height: 40px, Padding: 10px 20px
- Background: Transparent
- Icon: 🆓 (16px, 8px margin-right)
- Text: "Unpaid" (14px, regular, #6c757d)
- Hover: Background #e9ecef

**Tab 3: Web Crawler** (inactive - only if checked)
- Height: 40px, Padding: 10px 20px
- Background: Transparent
- Icon: 🕷️ (16px, 8px margin-right)
- Text: "Web Crawler" (14px, regular, #6c757d)
- Hover: Background #e9ecef

**EDITOR AREA:**
- Width: 1576px
- Height: 600px (minimum, expandable)
- Background: White (#ffffff)
- Padding: 16px
- Font: Monospace (SF Mono, Consolas), 14px, line height 22px

**Editor Content** (mock prompt text with syntax highlighting):

```
Generate a news article for {{stock_symbol}} based on the following data:

## Earnings Information
{{earnings}}

## Sentiment Analysis
{{sentiment}}

## Recent Price Movement
{{prices}}

Instructions:
- Write in a professional, objective tone
- Highlight key metrics and changes
- Keep the article between 200-300 words
- Focus on data-driven insights

Output format: Plain text, structured with headings
```

**Syntax Highlighting:**
- Placeholders `{{variable}}`: Orange (#ce9178), bold
- Headings (##): Blue (#4ec9b0)
- Regular text: Dark gray (#212529)
- Comments/instructions: Green (#6a9955)

**Line Numbers:**
- Left gutter: 40px width
- Background: #f8f9fa
- Numbers: Gray (#6c757d), 12px font
- Current line highlight: Light blue background (#e7f1ff)

**VALIDATION PANEL** (below editor, collapsible):
- Width: 1576px
- Border-top: 1px solid #dee2e6
- Padding: 16px
- Background: White

**Validation Header:**
- Icon: Checkmark circle (green) or Warning triangle (yellow)
- Text: "All placeholders valid" or "2 warnings found"
- Font: 14px, medium
- Color: Success green or warning yellow

**Validation Issues List** (if warnings exist):
Create 2 warning items:

**Warning 1:**
- Icon: Warning triangle (16px, yellow)
- Message: "Placeholder {{market}} is not in available data sources"
- Line reference: "Line 12" (clickable, blue, 12px)
- 8px margin-bottom

**Warning 2:**
- Same layout
- Message: "Unused placeholder {{ratings}} - configured but not used in prompt"
- Line reference: "Line --"

**BOTTOM ACTIONS:**
Below validation panel, 16px margin-top:
- "Preview Final Prompt" button (primary blue, 180px width, 40px height)
- Helper text: "Test with: AAPL" (12px, #6c757d, 8px margin-left)

**After AI Generates:**
1. Create tabbed component with active/inactive tab states
2. Only show tabs for checked prompt types (Paid always visible)
3. Active tab: white background + blue bottom border
4. Inactive tabs: transparent background, gray text
5. Clicking tab switches editor content to that prompt type's template
6. Ensure monospace font is applied to editor text
7. Apply orange color (#ce9178) to all {{placeholder}} text
8. Create focus state for editor (blue border)
9. Add line number gutter on left
10. Create collapsed state for validation panel
11. Ensure "Preview Final Prompt" button is prominent
12. Add warning icon (⚠️) to tab if validation errors exist for that prompt
13. Each tab maintains its own editor state (content, cursor position, undo history)

---

### Prompt #11: Prompt Preview Modal

Create a modal that shows the final prompt with placeholders replaced by actual data.

**Modal Overlay:**
- Full screen (1920x1080px)
- Background: rgba(0, 0, 0, 0.5) - semi-transparent dark
- Z-index: High (above all content)

**Modal Container:**
- Width: 900px
- Max-height: 800px
- Background: White (#ffffff)
- Border-radius: 8px
- Shadow: 0 8px 24px rgba(0,0,0,0.2)
- Position: Centered (vertically and horizontally)

**Modal Header:**
- Height: 64px
- Background: Light gray (#f8f9fa)
- Border-bottom: 1px solid #dee2e6
- Border-radius: 8px 8px 0 0
- Padding: 20px 24px

Layout (horizontal, space-between):
- Title: "Prompt Preview" (20px, semi-bold, #212529)
- Stock ID badge: "AAPL" (14px, padding 6px 12px, background #e7f1ff, text #0d6efd, border-radius 4px)
- Close button: "×" (32px, gray, top-right corner)

**Modal Body:**
- Padding: 24px
- Max-height: 650px
- Overflow: Scroll (vertical)

**Tabs** (horizontal, 8px gap, margin-bottom 24px):
- Tab 1: "With Data" (active - blue underline, 2px thick)
- Tab 2: "Template Only" (inactive - gray text)

**Content Area - "With Data" Tab:**

**Preview Container:**
- Background: #f8f9fa
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Padding: 20px
- Font: 14px, line-height 24px

**Rendered Prompt Text** (with data substituted):

```
Generate a news article for AAPL based on the following data:

## Earnings Information
Symbol: AAPL
Quarter: Q4 2024
Revenue: $119.58B
EPS: $2.18
Earnings Date: October 31, 2024
Summary: Apple reported strong Q4 results with revenue beating expectations...

## Sentiment Analysis
Score: 0.78
Label: Positive
Confidence: High (92%)
Key phrases: strong results, beat expectations, positive outlook

## Recent Price Movement
Current: $178.45
1-week change: +$4.32 (2.48%)
1-month change: +$12.15 (7.31%)

Instructions:
- Write in a professional, objective tone
- Highlight key metrics and changes
- Keep the article between 200-300 words
- Focus on data-driven insights

Output format: Plain text, structured with headings
```

**Highlighting:**
- Substituted data: Light blue background (#e7f1ff)
- Headings: Bold, dark (#212529)
- Instructions: Regular weight

**Modal Footer:**
- Height: 72px
- Background: White
- Border-top: 1px solid #dee2e6
- Padding: 16px 24px
- Border-radius: 0 0 8px 8px

Layout (horizontal, space-between):
- Left: "Edit Prompt" button (secondary outline, 120px width)
- Right: "Copy to Clipboard" button (primary blue, 160px width)

**After AI Generates:**
1. Create both tab states (With Data active, Template Only inactive)
2. Create Template Only tab content (shows placeholders, not data)
3. Add subtle blue background to substituted data areas
4. Ensure close button (×) is clearly visible and clickable
5. Add scrollbar styling if content overflows

---

## PHASE 7: MODEL TESTING PANEL

### Prompt #12: Model Selection & Configuration Panel

Create a panel for selecting AI models and configuring generation settings.

**Panel Container:**
- Width: 1576px
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Panel Header:**
- Text: "Model Selection & Testing"
- Font: 20px, semi-bold, dark (#212529)
- Badge: "(Used for All Types)" (12px, light gray background #e9ecef, text #6c757d, padding 4px 8px, border-radius 12px, 8px margin-left)
- Margin-bottom: 8px

**Description:**
- Text: "Select one or more models to test across all checked prompt types. You can compare outputs side-by-side."
- Font: 14px, regular, #6c757d
- Margin-bottom: 8px

**Info Callout:**
- Background: Light blue (#e7f1ff)
- Border-left: 3px solid #0d6efd
- Padding: 12px 16px
- Border-radius: 4px
- Margin-bottom: 24px
- Icon: Info circle (16px, #0d6efd, left)
- Text: "Will generate for: Paid, Unpaid, Crawler (3 types × 2 models = 6 generations)" (14px, #212529, 12px margin-left from icon)
- Note: Text updates based on checked types and selected models

**MODEL CARDS:**
Create 3 model provider sections:

**Section 1: OpenAI Models**
- Subheading: "OpenAI" (16px, medium, #212529, margin-bottom 12px)

Create 2 model cards (horizontal layout, 16px gap):

**Model Card: GPT-4**
- Width: 500px
- Height: 160px
- Border: 2px solid #dee2e6
- Border-radius: 6px
- Padding: 16px
- Background: White

**Card Header:**
Checkbox (left, 20px square, blue when checked) + Model name "GPT-4" (18px, medium, #212529)

**Card Body** (8px margin-top):
Description: "Most capable model, best for complex reasoning" (14px, #6c757d)

**Settings** (16px margin-top):
Row 1:
- Label: "Temperature" (12px, #6c757d)
- Slider: 0 to 1, current value 0.7 (displayed above slider)
- Width: 200px

Row 2 (12px margin-top):
- Label: "Max Tokens" (12px, #6c757d)
- Input: Number input, value "500", width 100px

**Cost Estimate** (bottom-right):
- Text: "Estimated: ~$0.12 per generation"
- Font: 12px, #6c757d
- Icon: Info circle (tooltip on hover)

**POST-GENERATION METRICS** (shown after generation completes):
Below cost estimate, 12px margin-top
- Divider: 1px solid #dee2e6 (full card width, 8px margin-bottom)
- Container: Light gray background (#f8f9fa), padding 12px, border-radius 4px
- Label: "⚡ GENERATION METRICS" (12px, semi-bold, #212529, margin-bottom 8px)
- Metrics (vertical stack, 4px gap):
  - 🎯 Tokens: 456 (12px, #212529)
  - ⏱️ Time: 8.3s (12px, #212529) - Color indicator: green if <5s, yellow if 5-15s, red if >15s
  - 💰 Actual Cost: $0.08 (12px, semi-bold, #198754)
- Tooltip on hover: Shows breakdown "Prompt tokens: 234, Completion tokens: 222"

**Model Card: GPT-3.5 Turbo**
Same layout as GPT-4 card
- Description: "Faster and more cost-effective"
- Default temperature: 0.7
- Default tokens: 500
- Cost: "~$0.02 per generation"

**Section 2: Anthropic Models**
Same layout as Section 1

**Model Card: Claude 3 Sonnet**
Same card layout
- Description: "Balanced performance and speed"
- Cost: "~$0.08 per generation"
- Checkbox: Checked (selected)

**Model Card: Claude 3 Opus**
Same card layout
- Description: "Most powerful model for complex tasks"
- Cost: "~$0.15 per generation"

**Section 3: Google Models**
Same layout

**Model Card: Gemini Pro**
Same card layout
- Description: "Fast and efficient for most tasks"
- Cost: "~$0.05 per generation"

**COST SUMMARY SECTION:**
Below all model cards, 24px margin-top:

**Container:**
- Width: 100%
- Background: Light yellow (#fff3cd)
- Border-left: 4px solid #ffc107
- Padding: 16px 20px
- Border-radius: 4px

Layout (horizontal, space-between):
- LEFT:
  - Text: "Selected models: 2" (14px, #212529)
  - Text: "GPT-4, Claude 3 Sonnet" (14px, #6c757d, 4px margin-top)
- RIGHT:
  - Text: "Estimated cost:" (14px, #6c757d)
  - Value: "$0.20" (24px, semi-bold, #212529, 4px margin-top)

**GENERATE BUTTON:**
Below cost summary, 24px margin-top:
- Button: "Generate with Selected Models"
- Style: Primary blue (#0d6efd), white text, semi-bold
- Width: 100% (full width)
- Height: 56px (large, prominent)
- Border-radius: 6px
- Icon: Sparkles/magic icon (20px, left, 12px margin-right)
- Font: 18px

**Disabled State** (if no models selected):
- Background: #e9ecef
- Text: #6c757d
- Cursor: not-allowed
- Tooltip: "Select at least one model to generate"

**After AI Generates:**
1. Create checkbox component with checked/unchecked states
2. Create slider component for temperature
3. Ensure cost values are prominently displayed (estimated before, actual after)
4. Create disabled state for generate button
5. Add hover states for all interactive elements
6. Create loading state for generate button (spinner + "Generating...")
7. **Create hidden/shown state for POST-GENERATION METRICS section** (hidden initially, shown after generation)
8. Update info callout text dynamically based on checked types and selected models
9. Cost estimate shows per-generation, metrics show actual per-type (if multiple types selected)
10. Metrics container should clearly distinguish from pre-generation estimate with background color
11. Performance color indicators for time: green (<5s), yellow (5-15s), red (>15s)

---

## PHASE 8: RESULTS & COMPARISON PANEL

### Prompt #13: Grouped Generation Results (By Prompt Type → Model)

Create a results panel showing generated news grouped by prompt type, then by model.

**Panel Container:**
- Width: 1576px (full content width)
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Panel Header:**
- Text: "Generation Results"
- Font: 24px, semi-bold, dark (#212529)
- Margin-bottom: 8px

**Subheading:**
- Text: "Compare outputs from different models across prompt types"
- Font: 14px, regular, #6c757d
- Margin-bottom: 24px

**GENERATION STATUS BAR** (shown during generation):
- Width: 100%
- Height: 60px
- Background: Light blue (#e7f1ff)
- Border-left: 4px solid #0d6efd
- Padding: 16px 20px
- Border-radius: 4px
- Margin-bottom: 24px

Layout (horizontal, aligned center):
- LEFT:
  - Spinner icon (24px, blue, animated rotation)
  - Text: "Generating news articles..." (16px, medium, #0d6efd, 12px margin-left)
- RIGHT:
  - Progress: "1 of 2 models complete" (14px, #6c757d)

**GROUPED RESULTS DISPLAY** (after generation complete):

Results organized hierarchically: Prompt Type → Models (within each type)

---

**PROMPT TYPE GROUP: PAID RESULTS**

**Group Header** (collapsible):
- Width: 100%
- Height: 56px
- Background: Light blue (#e7f1ff)
- Border-left: 4px solid #0d6efd
- Padding: 16px 20px
- Border-radius: 6px 6px 0 0
- Cursor: pointer (entire header clickable to collapse/expand)
- Margin-bottom: 16px

Layout:
- LEFT:
  - Icon: 💰 (20px, 8px margin-right)
  - Text: "PAID RESULTS" (18px, semi-bold, #0d6efd)
- RIGHT:
  - Collapse icon: Chevron-down (16px, #0d6efd, rotates when collapsed)

**Results Grid Within Paid Group:**
Create 2 result columns (16px gap between, equal width):

**Column 1 - GPT-4 Result (Paid):**
- Width: 780px (half of 1576px minus gap)
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Background: White

**Column Header** (sticky on scroll):
- Height: 56px
- Background: Light gray (#f8f9fa)
- Border-bottom: 1px solid #dee2e6
- Padding: 16px 20px
- Border-radius: 6px 6px 0 0

Layout (horizontal, space-between):
- LEFT:
  - Model name: "GPT-4" (16px, semi-bold, #212529)
  - Settings: "temp: 0.7 | tokens: 500" (12px, #6c757d, 4px margin-top)
- RIGHT:
  - Status badge: "Success" (success green, 12px, padding 4px 8px, border-radius 12px)
  - Copy button: Icon-only (clipboard icon, 32px square, gray, hover blue)

**Column Body** (scrollable):
- Padding: 20px
- Max-height: 600px
- Overflow: Scroll (vertical)

**Generated Text Content:**
```
Apple Reports Strong Q4 Earnings, Beating Expectations

Apple Inc. (AAPL) delivered robust fourth-quarter results on October 31, 2024, with revenue reaching $119.58 billion and earnings per share of $2.18, surpassing Wall Street forecasts.

Key Financial Highlights

The tech giant's Q4 2024 performance demonstrated continued momentum, with revenue beating analyst expectations. The company's EPS of $2.18 represents solid execution in a competitive market environment.

Market Sentiment and Price Action

Investor sentiment remains decidedly positive, with sentiment analysis showing a score of 0.78 and high confidence at 92%. The stock has shown strong recent performance, gaining $4.32 (2.48%) over the past week and $12.15 (7.31%) over the month, currently trading at $178.45.

Market analysts highlight key positive indicators including "strong results," "beat expectations," and a "positive outlook" as driving factors behind the favorable sentiment.

Outlook

With strong Q4 results and positive market sentiment, Apple continues to demonstrate its market leadership and ability to execute in a dynamic technology landscape.
```

**Text Styling:**
- Font: 15px, line-height 26px
- Headings (##): Bold, 18px, 12px margin-top/bottom
- Paragraphs: Regular weight, 12px margin-bottom
- Color: Dark (#212529)

**Column Footer** (sticky bottom):
- Height: 56px
- Background: Light gray (#f8f9fa)
- Border-top: 1px solid #dee2e6
- Padding: 12px 20px
- Border-radius: 0 0 6px 6px

Layout (horizontal, space-between):
Metadata items with icons (separated by vertical dividers):
- 🎯 Tokens: 456 (14px, #212529)
- ⏱️ Time: 8.3s (14px, #212529) - Color: green if <5s, yellow if 5-15s, red if >15s
- 💰 Cost: $0.08 (14px, semi-bold, #198754)
- Rating: 5-star component (3.5 stars filled, gold #ffc107)

**Column 2 - Claude 3 Sonnet Result (Paid):**
Same layout as Column 1
- Model name: "Claude 3 Sonnet"
- Different generated text content (similar news article but with variation)
- Metadata: 🎯 412 | ⏱️ 6.7s (green) | 💰 $0.06
- Rating: 5-star component (4 stars filled)

---

**PROMPT TYPE GROUP: UNPAID RESULTS** (shown only if Unpaid was checked)

**Group Header** (collapsible):
- Same layout as Paid header
- Background: Light green (#d1f4e0)
- Border-left: 4px solid #198754
- Icon: 🆓 (20px)
- Text: "UNPAID RESULTS" (18px, semi-bold, #198754)
- Margin-top: 32px from previous group

**Results Grid Within Unpaid Group:**
Same 2-column layout as Paid group
- Column 1: GPT-4 Result (Unpaid)
- Column 2: Claude 3 Sonnet Result (Unpaid)
- Each with metadata: tokens, time, cost

---

**PROMPT TYPE GROUP: WEB CRAWLER RESULTS** (shown only if Crawler was checked)

**Group Header** (collapsible):
- Same layout as Paid header
- Background: Light orange (#fff3cd)
- Border-left: 4px solid #ffc107
- Icon: 🕷️ (20px)
- Text: "WEB CRAWLER RESULTS" (18px, semi-bold, #dc7609)
- Margin-top: 32px from previous group

**Results Grid Within Crawler Group:**
Same 2-column layout
- Column 1: GPT-4 Result (Crawler)
- Column 2: Claude 3 Sonnet Result (Crawler)
- Each with metadata: tokens, time, cost

---

**TOTAL COST SUMMARY** (below all groups):
Margin-top: 32px
- Container: Light blue background (#e7f1ff), padding 16px 24px, border-radius 4px
- Layout: Horizontal, space-between
- LEFT: "Total Generations: 6 (3 types × 2 models)" (14px, #212529)
- RIGHT: "Total Actual Cost: $0.48" (18px, semi-bold, #198754)

**COMPARISON ACTIONS** (below summary):
Margin-top: 24px

**Action Buttons** (horizontal, 16px gap):
- "Regenerate" button (secondary outline, 140px width, 40px height)
- "Save to Iteration History" button (secondary, 200px width)
- "Use for Publishing" dropdown (primary blue, 180px width) → Shows which model to use

**After AI Generates:**
1. Create loading/generating state variant with status bar showing total progress
2. Create completed state with grouped results visible
3. **Create collapsible group headers** for each prompt type (Paid, Unpaid, Crawler)
4. Only show groups for checked prompt types
5. Color-code each prompt type group (blue for Paid, green for Unpaid, orange for Crawler)
6. Ensure columns within each group are equal width with proper gap
7. Add copy button functionality indicator per result
8. Create 5-star rating component (fillable/editable)
9. Ensure sticky header and footer for columns within scrollable groups
10. Add scrollable body area with proper scrollbar styling
11. **Display metadata with icons**: 🎯 tokens, ⏱️ time (color-coded by speed), 💰 cost
12. Create total cost summary component at bottom
13. Groups collapsed by default except Paid (always expanded)
14. Smooth collapse/expand animation for group sections

---

### Prompt #14: Iteration History Timeline

Create a timeline showing previous generation attempts for comparison.

**Panel Container:**
- Width: 1576px
- Background: White (#ffffff)
- Border-radius: 8px
- Padding: 24px
- Shadow: 0 2px 4px rgba(0,0,0,0.08)
- Margin-bottom: 24px

**Panel Header** (collapsible):
- Icon: Chevron-down (16px, rotates when collapsed)
- Text: "Iteration History"
- Font: 20px, semi-bold, dark (#212529)
- Badge: "8 iterations" (12px, secondary gray background, white text, padding 4px 8px, border-radius 12px, 8px margin-left)
- Border-bottom: 1px solid #dee2e6
- Padding-bottom: 16px
- Margin-bottom: 24px

**Timeline Container** (expanded state):
- Vertical timeline with connecting line (2px solid #dee2e6, left aligned)

Create 5 timeline items (most recent to oldest):

**Timeline Item 1 (Most Recent - Active):**
- Container: Light blue background (#e7f1ff)
- Border-left: 4px solid #0d6efd (replaces timeline line)
- Padding: 16px 20px
- Border-radius: 4px
- Margin-bottom: 12px

Layout:
- TOP ROW (horizontal, space-between):
  - LEFT:
    - Timestamp: "2 minutes ago" (14px, #0d6efd, medium)
    - Badge: "Current" (12px, blue background, white text, padding 4px 8px, border-radius 12px, 8px margin-left)
  - RIGHT:
    - "View Details" link (14px, blue, underline on hover)

- MIDDLE ROW (8px margin-top):
  - Text: "Models: GPT-4, Claude 3 Sonnet" (14px, #212529)
  - Separator: "|" (8px margin left/right)
  - Text: "Stock: AAPL" (14px, #6c757d)

- BOTTOM ROW (8px margin-top):
  - Text: "Prompt changes: Updated earnings section instructions" (14px, italic, #6c757d)
  - Cost: "$0.20" (14px, #212529, semi-bold, 16px margin-left)

**Timeline Item 2:**
- Same layout as Item 1
- Background: White (not active)
- Border-left: 2px solid #dee2e6 (standard timeline)
- Timestamp: "1 hour ago"
- No "Current" badge
- Models: "GPT-4, GPT-3.5 Turbo"
- Stock: "AAPL"
- Changes: "Tested with different models"
- Cost: "$0.14"

**Timeline Item 3:**
Same layout
- Timestamp: "3 hours ago"
- Models: "Claude 3 Sonnet"
- Changes: "Initial prompt test"
- Cost: "$0.08"

**Timeline Item 4:**
Same layout
- Timestamp: "Yesterday at 3:42 PM"
- Models: "GPT-4"
- Changes: "Testing with Q3 earnings data"
- Cost: "$0.12"

**Timeline Item 5:**
Same layout
- Timestamp: "Yesterday at 2:15 PM"
- Models: "GPT-4, Claude 3 Opus"
- Changes: "First generation attempt"
- Cost: "$0.27"

**Load More Section** (bottom):
- Button: "Load More Iterations" (secondary outline, 180px width, 40px height, centered)
- Text below: "Showing 5 of 8 iterations" (12px, #6c757d, centered, 8px margin-top)

**After AI Generates:**
1. Create collapsed state (header only, timeline hidden)
2. Create active/current iteration highlight (blue background)
3. Ensure timeline line connects items vertically
4. Add hover states for "View Details" links
5. Create expandable detail view for each iteration

---

## PHASE 9: PUBLISHING & CONFIRMATION

### Prompt #15: Publish Confirmation Modal

Create a confirmation modal for publishing configuration to production.

**Modal Overlay:**
- Full screen (1920x1080px)
- Background: rgba(0, 0, 0, 0.6) - semi-transparent dark
- Z-index: High

**Modal Container:**
- Width: 700px
- Background: White (#ffffff)
- Border-radius: 8px
- Shadow: 0 8px 32px rgba(0,0,0,0.3)
- Position: Centered

**Modal Header:**
- Height: 72px
- Background: White
- Border-bottom: 1px solid #dee2e6
- Padding: 24px
- Border-radius: 8px 8px 0 0

Layout:
- Icon: Warning triangle (24px, orange #ffc107, left)
- Title: "Publish Configuration to Production" (20px, semi-bold, #212529, 12px margin-left)
- Close button: "×" (32px, gray, top-right)

**Modal Body:**
- Padding: 24px
- Max-height: 500px
- Overflow: Scroll (vertical)

**Section 1: Validation Checklist**
Heading: "Pre-Publish Validation" (16px, medium, #212529, margin-bottom 12px)

Checklist (4 items, 8px gap):

**Item 1:**
- Icon: Checkmark circle (green, 20px)
- Text: "APIs configured (3 data sources)" (14px, #212529)

**Item 2:**
- Icon: Checkmark circle (green)
- Text: "Prompt created and validated (no errors)" (14px, #212529)

**Item 3:**
- Icon: Checkmark circle (green)
- Text: "Tested with models (2 successful generations)" (14px, #212529)

**Item 4:**
- Icon: Warning triangle (yellow, 20px)
- Text: "Last test was 2 hours ago" (14px, #212529)
- Helper text: "Consider re-testing before publishing" (12px, italic, #6c757d, 24px margin-left)

**Section 2: Configuration Summary** (24px margin-top)
Heading: "Configuration Summary" (16px, medium, #212529, margin-bottom 12px)

**Summary Container:**
- Background: Light gray (#f8f9fa)
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Padding: 16px

Summary items (table-like layout):
- Row 1: "Trigger Name" (label, #6c757d) | "Earnings Alert" (value, #212529)
- Row 2: "Data Sources" | "Earnings API, Sentiment Analysis API, Historical Prices API"
- Row 3: "Model" | "Claude 3 Sonnet (temp: 0.7, tokens: 500)"
- Row 4: "Section Order" | "1. Earnings, 2. Sentiment, 3. Prices"
- Row 5: "Prompt Length" | "1,247 characters"

**Section 3: Diff Preview** (24px margin-top)
Heading: "Changes from Current Production" (16px, medium, #212529, margin-bottom 12px)

**Diff Container:**
- Background: White
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Padding: 16px
- Max-height: 200px
- Overflow: Scroll

**Diff Content** (side-by-side or unified diff):
Show 2-3 change blocks:

**Change 1:**
- Line reference: "Line 8-10" (12px, #6c757d)
- Old text (red background #ffebe9, strikethrough): "Focus on earnings metrics"
- New text (green background #e6f4ea): "Highlight key metrics and changes"

**Change 2:**
- Line reference: "Line 15"
- Old text: "Keep article concise"
- New text: "Keep the article between 200-300 words"

**Warning Message** (24px margin-top):
- Container: Yellow background (#fff3cd)
- Border-left: 4px solid #ffc107
- Padding: 12px 16px
- Border-radius: 4px

Icon: Warning triangle (16px, orange) + Text: "This will replace the current production configuration (v1.2). The previous version will be saved in configuration history." (14px, #212529)

**Modal Footer:**
- Height: 80px
- Background: Light gray (#f8f9fa)
- Border-top: 1px solid #dee2e6
- Padding: 20px 24px
- Border-radius: 0 0 8px 8px

Layout (horizontal, space-between):
- LEFT:
  - "Cancel" button (secondary outline, 120px width, 40px height)
- RIGHT:
  - "Publish to Production" button (danger red #dc3545, white text, semi-bold, 200px width, 40px height)
  - Icon: Upload icon (16px, left, 8px margin-right)

**After AI Generates:**
1. Create warning state for checklist items (yellow triangle)
2. Create diff highlighting (red for removed, green for added)
3. Ensure publish button uses danger color (red) to indicate caution
4. Add hover states for buttons
5. Create scrollable body if content exceeds max-height
6. Add keyboard shortcuts (Escape to cancel, Enter to publish with focus)

---

### Prompt #16: Publishing Success State

Create a success confirmation screen after publishing.

**Modal Container:**
- Width: 600px
- Background: White (#ffffff)
- Border-radius: 8px
- Shadow: 0 8px 32px rgba(0,0,0,0.3)
- Position: Centered
- Padding: 40px

**Success Icon:**
- Large checkmark circle (80px diameter)
- Color: Success green (#198754)
- Background: Light green (#d1f4e0)
- Border-radius: 50%
- Centered horizontally
- Margin-bottom: 24px

**Success Message:**
- Title: "Configuration Published Successfully" (24px, semi-bold, #212529, centered)
- Margin-bottom: 12px

**Details:**
- Text: "Version 1.3 is now live in production" (16px, #6c757d, centered)
- Margin-bottom: 32px

**Metadata Box:**
- Background: Light gray (#f8f9fa)
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Padding: 20px
- Margin-bottom: 32px

Metadata items (centered, 12px gap between):
- "Published by: John Doe" (14px, #212529)
- "Timestamp: October 28, 2025 at 10:34 AM" (14px, #6c757d)
- "Version: 1.3" (14px, #212529)
- "Previous version: 1.2" (14px, #6c757d)

**Action Buttons** (horizontal, centered, 16px gap):
- "View Published Config" button (primary blue, 180px width, 40px height)
- "Return to Dashboard" button (secondary outline, 180px width, 40px height)

**Auto-close Timer:**
- Text: "This dialog will close in 5 seconds..." (12px, #6c757d, centered, 16px margin-top)

**After AI Generates:**
1. Ensure success icon is prominent and centered
2. Create auto-dismiss animation (fades out after 5s)
3. Add confetti or subtle celebration animation (optional)
4. Ensure buttons are clearly visible and accessible

---

## PHASE 10: CONFIGURATION HISTORY

### Prompt #17: Configuration History Side-Drawer

Create a side-drawer panel showing configuration version history.

**Drawer Overlay:**
- Full screen (1920x1080px)
- Background: rgba(0, 0, 0, 0.3) - semi-transparent
- Clickable to close drawer

**Drawer Container:**
- Width: 600px
- Height: 100% (full viewport height)
- Background: White (#ffffff)
- Position: Right side (slides in from right)
- Shadow: -4px 0 16px rgba(0,0,0,0.1)

**Drawer Header:**
- Height: 72px
- Background: White
- Border-bottom: 1px solid #dee2e6
- Padding: 24px
- Position: Sticky top

Layout (horizontal, space-between):
- Title: "Configuration History" (20px, semi-bold, #212529)
- Close button: "×" (32px, gray, hover dark)

**Drawer Body** (scrollable):
- Padding: 24px
- Overflow: Scroll (vertical)

**Version List:**
Create 5 version cards (16px gap between):

**Version Card 1 (Current Production):**
- Width: 100% (552px after padding)
- Border: 2px solid #198754 (green - indicates active)
- Border-radius: 6px
- Padding: 20px
- Background: Light green (#f0f9f4)

**Card Header:**
Layout (horizontal, space-between):
- LEFT:
  - Version: "Version 1.3" (18px, semi-bold, #212529)
  - Badge: "Production" (12px, success green background, white text, padding 4px 8px, border-radius 12px, 8px margin-left)
- RIGHT:
  - Timestamp: "2 hours ago" (14px, #6c757d)

**Card Body** (12px margin-top):
- Published by: "John Doe" (14px, #6c757d)
- Models: "Claude 3 Sonnet" (14px, #212529, 4px margin-top)
- APIs: "3 data sources" (14px, #6c757d, 4px margin-top)
- Prompt summary: "Updated earnings section instructions..." (14px, #6c757d, italic, 8px margin-top, truncated with ellipsis)

**Card Actions** (16px margin-top):
Horizontal buttons (8px gap):
- "View Details" button (secondary outline, 110px width, 36px height)
- "Compare" button (secondary outline, 100px width, 36px height)

**Version Card 2:**
Same layout as Card 1
- Border: 1px solid #dee2e6 (standard - not active)
- Background: White
- Version: "Version 1.2"
- No "Production" badge
- Timestamp: "Yesterday at 4:15 PM"
- Published by: "Jane Smith"
- Models: "GPT-4"
- Add "Rollback" button (danger red outline, 100px width, 36px height) to actions

**Version Card 3:**
Same layout
- Version: "Version 1.1"
- Timestamp: "3 days ago"
- Published by: "John Doe"
- Models: "Claude 3 Sonnet, GPT-4"

**Version Card 4:**
Same layout
- Version: "Version 1.0"
- Timestamp: "1 week ago"
- Published by: "Jane Smith"
- Badge: "Initial" (secondary gray, 8px margin-left from version)

**Pagination/Load More:**
- Button: "Load More Versions" (secondary outline, 160px width, 40px height, centered)
- Text: "Showing 4 of 12 versions" (12px, #6c757d, centered, 8px margin-top)

**After AI Generates:**
1. Create slide-in animation for drawer (from right)
2. Highlight active production version with green border
3. Create hover states for action buttons
4. Ensure drawer is scrollable with smooth scrollbar
5. Add close-on-click for overlay background
6. Create expanded detail view variant for "View Details" action

---

### Prompt #18: Version Comparison View (Diff)

Create a side-by-side comparison view for two configuration versions.

**Container:** (Replaces version list in drawer when "Compare" is clicked)
- Width: 600px (same as drawer)
- Padding: 24px

**Comparison Header:**
- Text: "Comparing Versions" (20px, semi-bold, #212529)
- Margin-bottom: 24px

**Version Selectors:**
Layout (horizontal, 16px gap):

**Selector 1:**
- Label: "Version A" (12px, #6c757d, above)
- Dropdown: "Version 1.3 (Current)" (selected)
- Width: 268px
- Height: 40px
- Border: 1px solid #ced4da
- Border-radius: 4px

**Selector 2:**
- Label: "Version B"
- Dropdown: "Version 1.2"
- Same styling as Selector 1

**Diff Content Area** (24px margin-top):
Tabs (horizontal, 8px gap):
- "Prompt" (active - blue underline)
- "APIs" (inactive - gray text)
- "Model Settings" (inactive)
- "Metadata" (inactive)

**Diff Display - Prompt Tab** (side-by-side layout):

**Container:**
- Background: White
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Padding: 16px
- Max-height: 600px
- Overflow: Scroll

Create 2 columns (2px gap, equal width):

**Column 1 - Version 1.3:**
- Header: "Version 1.3" (14px, medium, #212529, background #f8f9fa, padding 8px, border-radius 4px 4px 0 0)

**Diff Content:**
Display line-by-line text with highlighting:

Line 1: "Generate a news article for {{stock_symbol}}..." (no change - gray background #f8f9fa)
Line 2: "## Earnings Information" (no change)
Line 3: "{{earnings}}" (no change)
Line 4: "" (blank line)
Line 5: "Instructions:" (no change)
Line 6: "- Highlight key metrics and changes" (ADDED - green background #e6f4ea, green left border 3px)
Line 7: "- Keep the article between 200-300 words" (MODIFIED - yellow background #fff9e6, yellow left border 3px)

**Column 2 - Version 1.2:**
Same layout, showing corresponding lines:
Line 6: (blank - this line didn't exist) (REMOVED indication - red background #ffebe9)
Line 7: "- Keep article concise" (MODIFIED - yellow background, yellow left border)

**Legend** (below diff, 16px margin-top):
Horizontal items (16px gap):
- Green square (12px) + "Added" (12px, #6c757d)
- Yellow square + "Modified"
- Red square + "Removed"
- Gray square + "Unchanged"

**Actions** (24px margin-top):
- "Close Comparison" button (secondary, 140px width, 40px height)
- "Rollback to Version 1.2" button (danger red outline, 180px width, 40px height, 16px margin-left)

**After AI Generates:**
1. Create all tab variants (Prompt, APIs, Model Settings, Metadata)
2. Apply color-coded highlighting (green=added, yellow=modified, red=removed)
3. Ensure side-by-side columns align line numbers
4. Add line numbers on left (gray, 12px font)
5. Create smooth tab switching animation
6. Ensure scrollable content with synchronized scrolling for both columns

---

## PHASE 11: EMPTY STATES & ERROR SCREENS

### Prompt #19: Empty State - No Triggers

Create an empty state screen when no triggers are configured.

**Container:**
- Width: 600px
- Center aligned (vertically and horizontally on page)
- Padding: 40px

**Empty State Illustration:**
- Icon: Large inbox/folder icon (120px, light gray #dee2e6)
- Or: Simple illustration (can be replaced with actual illustration)
- Centered
- Margin-bottom: 24px

**Empty State Message:**
- Title: "No Triggers Available" (24px, semi-bold, #212529, centered)
- Margin-bottom: 12px

**Description:**
- Text: "There are currently no news triggers set up in the system. Contact your administrator to create triggers."
- Font: 16px, regular, #6c757d, centered
- Max-width: 400px, centered
- Line-height: 24px
- Margin-bottom: 32px

**Action Button:**
- Button: "Contact Administrator"
- Style: Secondary outline, 180px width, 44px height
- Icon: Mail icon (16px, left, 8px margin-right)
- Centered

**After AI Generates:**
1. Ensure perfect vertical and horizontal centering
2. Create illustration placeholder (can be replaced)
3. Add subtle animation (icon fades in)

---

### Prompt #20: Error State - API Failure

Create an error state component for API failures and network issues.

**Error Container:**
- Width: 500px
- Background: Light red (#ffebe9)
- Border-left: 4px solid #dc3545 (danger red)
- Border-radius: 4px
- Padding: 20px 24px

**Error Icon:**
- Icon: X-circle or alert triangle (32px, danger red #dc3545)
- Left aligned
- Float left with 16px margin-right

**Error Content:**
- Title: "Failed to Load Data" (18px, semi-bold, #dc3545)
- Margin-bottom: 8px

**Error Message:**
- Text: "Unable to fetch data from Earnings API. The request timed out after 5 seconds."
- Font: 14px, regular, #212529
- Line-height: 20px
- Margin-bottom: 16px

**Error Details** (collapsible):
- Link: "View technical details" (14px, blue, underline on hover)
- Expanded content (when clicked):
  - Background: White
  - Border: 1px solid #dee2e6
  - Border-radius: 4px
  - Padding: 12px
  - Font: Monospace, 12px, #6c757d
  - Text: "Error code: ETIMEDOUT\nEndpoint: /api/earnings/AAPL\nTimestamp: 2025-10-28T10:34:22Z"

**Action Buttons** (horizontal, 12px gap):
- "Retry" button (primary, 100px width, 36px height)
- "Dismiss" button (secondary outline, 100px width, 36px height)

**After AI Generates:**
1. Create variants for different error types (timeout, 404, 500, network)
2. Add collapsible technical details section
3. Ensure error is visually distinct with red color scheme
4. Add retry button loading state

---

## PHASE 12: LOADING STATES

### Prompt #21: Loading Skeleton for Configuration Workspace

Create skeleton loading placeholders for the Configuration Workspace.

**Skeleton Layout:**
Matches Configuration Workspace layout structure:

**Left Sidebar Skeleton:**
- Width: 280px
- Background: White
- Padding: 24px 16px

Create 5 skeleton items (vertical stack, 16px gap):
Each item:
- Width: 100%
- Height: 48px
- Background: Linear gradient animation (shimmer effect)
- Colors: #f8f9fa → #e9ecef → #f8f9fa (animates left to right)
- Border-radius: 4px

**Main Content Skeleton:**
- Width: 1576px
- Padding: 32px

**Header Skeleton:**
- Width: 300px (random width for text placeholder)
- Height: 32px
- Background: Shimmer gradient
- Border-radius: 4px
- Margin-bottom: 24px

**Panel Skeletons** (3 panels, 24px gap):

**Panel 1:**
- Width: 100%
- Height: 200px
- Background: White
- Border-radius: 8px
- Padding: 24px

Internal skeleton elements:
- Title bar: Width 200px, height 20px, shimmer
- Content lines: 3 lines (width 100%, 80%, 60%), height 16px each, 12px gap, shimmer

**Panel 2:**
Same layout, height 400px

**Panel 3:**
Same layout, height 300px

**Shimmer Animation:**
- Duration: 1.5s
- Easing: Linear
- Infinite loop
- Gradient moves from left (-100%) to right (100%)

**After AI Generates:**
1. Apply shimmer/pulse animation to all skeleton elements
2. Match exact positioning of actual content
3. Create variants for different loading states (initial load, content refresh)
4. Ensure animation is smooth and performant

---

## FINAL CHECKLIST & INTEGRATION

### Post-Generation Tasks

After generating all 21 prompts, perform the following integration tasks:

1. **Component Organization:**
   - Move all reusable components to "Components" page
   - Create component library with variants
   - Name all components consistently (PascalCase)

2. **Create Design System:**
   - Document color styles
   - Create text styles for all typography
   - Set up spacing/layout grid (8px base)
   - Create effect styles (shadows, borders)

3. **Build Interactive Prototype:**
   - Link Dashboard → Configuration Workspace (click "Configure" button)
   - Link Configuration Workspace sidebar items → respective panels
   - Link "Publish" button → Publish Confirmation Modal
   - Link "View History" → Configuration History Drawer
   - Link "Generate" button → Loading state → Results panel
   - Link breadcrumbs to navigate back

4. **Create Responsive Variants:**
   - Desktop (1920x1080) - Primary
   - Desktop (1366x768) - Secondary
   - Tablet (1024x768) - Stacked layout
   - Mobile message screen (< 768px) - "Use desktop" message

5. **Accessibility Check:**
   - Verify color contrast ratios (use Figma plugins)
   - Add keyboard navigation indicators
   - Include focus states for all interactive elements
   - Add ARIA labels to icon-only buttons

6. **Documentation:**
   - Create README in Figma file with:
     - How to navigate the prototype
     - Component usage guidelines
     - Color palette reference
     - Typography scale
     - Spacing system

7. **Developer Handoff Preparation:**
   - Inspect all components for CSS properties
   - Export all icons as SVG
   - Document interactive states (hover, active, focus, disabled)
   - Create component spec sheets with measurements

---

## Quick Reference

### Color Palette
- Primary Blue: `#0d6efd`
- Success Green: `#198754`
- Warning Yellow: `#ffc107`
- Danger Red: `#dc3545`
- Info Cyan: `#0dcaf0`
- Secondary Gray: `#6c757d`
- Light Gray: `#f8f9fa`
- Border Gray: `#dee2e6`
- Dark: `#212529`

### Typography Scale
- H1: 40px (2.5rem)
- H2: 32px (2rem)
- H3: 28px (1.75rem)
- H4: 24px (1.5rem)
- H5: 20px (1.25rem)
- Body: 16px (1rem)
- Small: 14px (0.875rem)
- Tiny: 12px (0.75rem)

### Spacing
- Base unit: 8px
- Common values: 8px, 12px, 16px, 24px, 32px, 40px, 48px

### Common Component Sizes
- Button height: 40px (standard), 48px (large), 36px (small)
- Input height: 40px
- Navbar height: 64px
- Modal header/footer: 72px
- Card padding: 24px
- Panel padding: 24px

---

## Estimated Time

**Total Figma Generation Time:** ~5-6 hours (MVP Scope)
- Phase 1-2 (Foundation & Dashboard): 1 hour
- Phase 3-4 (Workspace & Data Config): 1.5 hours
- Phase 5-6 (Section Mgmt & Prompt Editor): 1.5 hours
- Phase 7-8 (Model Testing & Results): 1.5 hours
- Phase 9-10 (Publishing & History): 1 hour
- Phase 11-12 (Empty/Error/Loading States): 0.5 hours
- Integration & Prototype: 1 hour

**Recommended Workflow:**
- Day 1: Phases 1-4 (Foundation through Data Config)
- Day 2: Phases 5-8 (Section Mgmt through Results)
- Day 3: Phases 9-12 + Integration (Publishing through completion)

---

## Notes

- These prompts are designed for Figma AI (Make Designs feature)
- Each prompt is copy-paste ready
- Manual adjustments may be needed after AI generation (see "After AI Generates" sections)
- Screenshots and mockups should be exported at 2x resolution for developer handoff
- Consider creating a Figma Dev Mode setup for seamless developer collaboration

---

## PHASE 12: REUSABLE COMPONENTS

### Prompt #22: Type Selection Checkbox Component

Create a reusable checkbox component for selecting prompt types (Paid, Unpaid, Web Crawler).

**Component: Type Selection Checkbox Group**

**Container:**
- Layout: Horizontal flex, 24px gap between checkboxes
- Width: Auto (fits content)
- Used in: Trigger Context Bar (Prompt #5)

**Label** (above checkboxes):
- Text: "Prompt Types" (14px, medium, #6c757d)
- Margin-bottom: 8px

---

**Checkbox Item 1: Paid** (default - always checked, disabled)

**Layout:** Horizontal flex, 8px gap, align-center

**Checkbox:**
- Size: 20px × 20px
- State: Checked (cannot be unchecked)
- Background: Blue (#0d6efd)
- Border: 2px solid #0d6efd
- Checkmark: White, 14px
- Cursor: not-allowed (disabled)
- Border-radius: 4px

**Icon:**
- Emoji: 💰 (16px)
- Margin-right: 8px

**Label:**
- Text: "Paid" (14px, semi-bold, #212529)
- Margin-left: 8px from checkbox

**Badge:**
- Text: "Default" (11px, medium)
- Background: Light blue (#e7f1ff)
- Text color: #0d6efd
- Padding: 2px 6px
- Border-radius: 8px
- Margin-left: 8px from label

---

**Checkbox Item 2: Unpaid** (optional - unchecked by default)

**Layout:** Same as Item 1

**Checkbox:**
- Size: 20px × 20px
- State: Unchecked (clickable)
- Background: White
- Border: 2px solid #ced4da
- Cursor: pointer
- Border-radius: 4px
- Hover: Border color #0d6efd

**Checked State:**
- Background: Blue (#0d6efd)
- Border: 2px solid #0d6efd
- Checkmark: White, 14px

**Icon:**
- Emoji: 🆓 (16px)
- Margin-right: 8px

**Label:**
- Text: "Unpaid" (14px, regular, #212529)
- Margin-left: 8px from checkbox

---

**Checkbox Item 3: Web Crawler** (optional - unchecked by default)

**Layout:** Same as Item 1

**Checkbox:**
- Size: 20px × 20px
- State: Unchecked (clickable)
- Background: White
- Border: 2px solid #ced4da
- Cursor: pointer
- Border-radius: 4px
- Hover: Border color #0d6efd

**Checked State:**
- Background: Blue (#0d6efd)
- Border: 2px solid #0d6efd
- Checkmark: White, 14px

**Icon:**
- Emoji: 🕷️ (16px)
- Margin-right: 8px

**Label:**
- Text: "Web Crawler" (14px, regular, #212529)
- Margin-left: 8px from checkbox

---

**Helper Text** (below all checkboxes):
- Margin-top: 8px
- Text: "Select the prompt types to configure and test. Paid is always included." (12px, italic, #6c757d)

**Interaction Behavior:**
1. Paid checkbox: Always checked, disabled (cannot be unchecked), grayed cursor
2. Unpaid checkbox: Toggleable, clicking checks/unchecks
3. Web Crawler checkbox: Toggleable, clicking checks/unchecks
4. Checking a type shows corresponding tab in Prompt Editor (Prompt #10)
5. Unchecking a type hides corresponding tab
6. At least one type must always be selected (Paid cannot be unchecked)

**Component States:**
- **State 1: Default** - Only Paid checked
- **State 2: Paid + Unpaid** - Paid and Unpaid checked
- **State 3: Paid + Crawler** - Paid and Crawler checked
- **State 4: All Three** - All checkboxes checked

**After AI Generates:**
1. Create all four component states (variants)
2. Ensure Paid checkbox has disabled visual treatment (slightly grayed)
3. Create hover states for Unpaid and Crawler checkboxes
4. Ensure checkmark animation on click
5. Create focus states (blue outline) for keyboard navigation
6. Icon + Text + Badge alignment must be pixel-perfect
7. Component should be easily reusable in Auto Layout

---

**MVP Scope:**
- This document covers the core configuration workflow only
- Audit Log and Settings screens removed from MVP scope
- Total: 22 prompts (updated for multi-type support) focusing on essential features
- Navigation simplified to Dashboard + Configuration Workspace only

**Version:** 2.3 (Multi-Type Prompt Support)
**Last Updated:** October 29, 2025
**Author:** UX Expert (Sally) & Product Manager (John)

**Changelog:**
- v2.3 (Oct 29, 2025): **MAJOR UPDATE** - Added multi-type prompt support (Paid, Unpaid, Crawler)
  - Updated Prompt #5: Added Type Selection checkboxes to Trigger Context Bar
  - Updated Prompt #10: Monaco Editor now has tabbed interface for switching between prompt types
  - Updated Prompt #12: Model Selection shows metadata (tokens, time, cost) after generation, marked as shared across all types
  - Updated Prompt #13: Results now grouped by Prompt Type → Model with collapsible sections
  - Added Prompt #22: Reusable Type Selection Checkbox Component
  - Total prompts: 22 (increased from 21)
- v2.2 (Oct 28, 2025): Added backend default selections, renamed button to "Use This Data", updated Trigger Context Bar with status badges, updated Section Management to show only selected sections
- v2.1 (Oct 28, 2025): Updated Prompt #6 - Data Configuration now uses multi-select dropdown with checkboxes for 14 hardcoded data sections instead of "Add API" pattern
- v2.0 (Oct 28, 2025): MVP scope with Dashboard dropdown selector
- v1.0: Initial version with card-based dashboard
