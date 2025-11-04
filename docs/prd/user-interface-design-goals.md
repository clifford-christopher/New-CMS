# User Interface Design Goals

### Overall UX Vision

The News CMS should feel like a **powerful yet approachable workspace** for content professionals. The interface must balance sophistication (handling complex data, prompts, and AI models) with clarity (no coding required). Think of a blend between:

- **Data exploration tools** (clear visualization of JSON structures, collapsible sections, syntax highlighting)
- **Creative workspaces** (prompt editor as the centerpiece, real-time previews)
- **Testing environments** (side-by-side model comparisons, diff views for iterations)

The user should always understand where they are in the workflow (trigger → data → prompt → generate → publish), what data is being used, and feel confident that testing before publishing prevents production errors. The experience should support rapid iteration: make a change, regenerate, compare—in seconds, not minutes.

### Key Interaction Paradigms

- **Progressive Disclosure**: Start with trigger selection and stock ID input; progressively reveal data APIs → parsed data → prompt editing → model selection as the user advances
- **Live Preview Everywhere**: Show real-time preview of structured data, final prompts with substituted values, and cost estimates before generation
- **Multi-Panel Layout**: Split screen showing configuration (left) and results/previews (right) to minimize context switching
- **Drag-and-Drop for Ordering**: Intuitive reordering of data sections without forms or save buttons
- **Side-by-Side Comparison**: Generated news from different models displayed in columns for easy visual comparison
- **Inline Editing with Instant Feedback**: Edit prompts or data with immediate validation (placeholder errors, syntax issues)
- **Confirmation Gates**: Explicit confirmation dialogs before publishing to production, showing exactly what will be saved

### Core Screens and Views

1. **Trigger Selection Dashboard**: List of available triggers with status indicators (configured/unconfigured, last updated, production status)
2. **Configuration Workspace** (main screen): Multi-panel layout with:
   - Stock ID input and trigger context (top)
   - API configuration panel (add/remove APIs, view raw JSON)
   - Data structuring panel (parsed data sections, drag-to-reorder)
   - Prompt editor (syntax highlighting, placeholder validation, preview)
   - Model selection panel (checkboxes for models, settings sliders, cost estimates)
3. **Generation Results View**: Side-by-side comparison of news output from different models with metadata (time, tokens, cost)
4. **Iteration History Panel**: Timeline/list of previous generations in current session showing what changed
5. **Publish Confirmation Modal**: Summary of configuration being published with validation checklist
6. **Configuration History/Audit Log Screen**: View past published configurations with diff capability

### Multi-Type Prompt Management

The CMS supports three independent prompt types (paid, unpaid, crawler) for different content distribution channels while maintaining a unified configuration interface:

**Type Selection Pattern:**
- Checkbox-based selection in Trigger Context Bar
- Paid prompt always visible and checked by default (primary audience)
- Unpaid and crawler prompts optional, shown when checked
- Clear visual indication of which types are active

**Unified Configuration Approach:**
- **Shared Components**: Data configuration, section management, and model selection apply to all prompt types (efficiency and consistency)
- **Separate Prompts**: Tabbed editor interface allows customizing prompt templates per type without duplication
- **Grouped Results**: Generation results organized by prompt type → model for clear comparison

**Tab Interaction Pattern:**
- Horizontal tabs (Paid | Unpaid | Crawler) for prompt editing
- Active tab highlighted with underline indicator
- Tab visibility driven by checkbox selection (unchecked types hidden)
- Single editor panel reduces screen clutter and scrolling

**Visual Hierarchy:**
- Type selection prominent but not intrusive (below stock ID input)
- Prompt tabs clearly labeled with type names and icons (💰 Paid, 🆓 Unpaid, 🕷️ Crawler)
- Generation results use colored headers per type for instant recognition

### Accessibility: None

As an internal tool for a small, specialized user group (content managers and analysts), accessibility compliance is not a business requirement for MVP. Basic browser accessibility (keyboard navigation, semantic HTML) should be followed as standard practice, but WCAG AA/AAA certification is out of scope.

### Branding

This is an internal tool, so corporate branding should be minimal and non-intrusive:
- Use company logo in header/navigation
- Follow corporate color palette for primary actions (if one exists)
- Focus on clean, professional UI that prioritizes readability and functionality over brand expression
- Rich text editor (Monaco or CodeMirror) should use a professional code theme (VS Code Dark+ or similar)

### Target Device and Platforms: Web Responsive (Desktop-first, Tablet Support)

- **Primary Target**: Desktop browsers (1920x1080 and 1366x768 resolutions)
- **Secondary Target**: Tablets in landscape orientation (iPad Pro, Surface)
- **Browser Support**: Chrome, Firefox, Safari, Edge (last 2 versions)
- **Mobile**: Explicitly out of scope for MVP (small screens cannot effectively display multi-panel comparisons and complex data structures)
- **Responsive Breakpoints**:
  - Desktop: 1200px+ (full multi-panel layout)
  - Tablet: 768px-1199px (panels stack or collapse, still usable but may require scrolling)
  - Below 768px: Display message suggesting desktop/tablet use
