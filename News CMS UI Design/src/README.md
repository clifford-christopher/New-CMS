# News CMS - AI-Powered News Generation System

A comprehensive content management system for configuring and managing AI-powered news generation triggers.

## 🎯 MVP Scope (v2.0)

This is the **Minimum Viable Product** focusing on the core configuration workflow:

### ✅ Included Features
- **Dashboard**: Dropdown-based trigger selection with quick stats
- **Configuration Workspace**: 5-step workflow for trigger configuration
  - Data Configuration (API selection and management)
  - Section Management (drag-and-drop reordering)
  - Prompt Engineering (Monaco-style editor)
  - Model Testing (multi-model selection)
  - Results & Comparison (side-by-side output comparison)
- **Publishing**: Confirmation modal with validation checklist
- **History**: Configuration version management drawer
- **UI States**: Empty states, error handling, loading skeletons

### ❌ Out of Scope for MVP
- Audit Log screen (future enhancement)
- Settings screen (future enhancement)
- User management (future enhancement)
- Advanced reporting (future enhancement)

## 🚀 Getting Started

The application is a single-page React application with two main views:

1. **Dashboard** - Select and manage triggers
2. **Configuration Workspace** - Configure selected trigger through 5-step workflow

## 🎨 Design System

### Color Palette
- **Primary Blue**: `#0d6efd`
- **Success Green**: `#198754`
- **Warning Yellow**: `#ffc107`
- **Danger Red**: `#dc3545`
- **Info Cyan**: `#0dcaf0`
- **Secondary Gray**: `#6c757d`
- **Light Gray**: `#f8f9fa`
- **Border Gray**: `#dee2e6`
- **Dark**: `#212529`

### Typography
- **H1**: 32px (Dashboard title)
- **H2**: 28px (Section headers)
- **H3**: 24px (Panel titles)
- **H4**: 20px (Subheadings)
- **Body**: 16px (Default text)
- **Small**: 14px (Metadata, labels)
- **Tiny**: 12px (Badges, helper text)

### Spacing
- Base unit: **8px**
- Common values: 8px, 12px, 16px, 24px, 32px, 40px, 48px

## 📁 Project Structure

```
/components
  ├── Dashboard.tsx              # Legacy dashboard (v1.0)
  ├── DashboardV2.tsx           # MVP Dashboard with dropdown selector
  ├── ConfigurationWorkspace.tsx # Main workspace container
  ├── Navbar.tsx                # Top navigation (dark theme)
  ├── Breadcrumb.tsx            # Navigation breadcrumbs
  
  # Configuration Panels
  ├── DataConfigurationPanel.tsx    # Step 1: API management
  ├── SectionManagementPanel.tsx    # Step 2: Section reordering
  ├── PromptEditor.tsx              # Step 3: Prompt template
  ├── ModelSelection.tsx            # Step 4: AI model selection
  ├── ResultsComparisonPanel.tsx    # Step 5: Output comparison
  
  # Supporting Components
  ├── ContextBar.tsx            # Trigger context bar
  ├── WorkflowSidebar.tsx       # 5-step navigation
  ├── BottomActionsBar.tsx      # Save/Publish actions
  ├── PublishModal.tsx          # Publish confirmation
  ├── HistoryDrawer.tsx         # Version history
  
  # UI States
  ├── EmptyState.tsx            # Empty state component
  ├── ErrorState.tsx            # Error display
  ├── LoadingSkeleton.tsx       # Loading placeholders
  
  # Future/Non-MVP (kept for reference)
  ├── AuditLogScreen.tsx        # Not in MVP
  ├── SettingsScreen.tsx        # Not in MVP
```

## 🔄 User Flow

### 1. Dashboard
- User views list of available triggers in a dropdown
- Quick stats show: Total Triggers, Configured Count, Last Updated
- Recent activity table shows configuration changes
- Select a trigger and click "Configure Selected Trigger"

### 2. Configuration Workspace
User progresses through 5 steps:

**Step 1: Data Configuration**
- Select APIs to fetch data from
- View raw JSON responses
- See structured data preview

**Step 2: Section Management**
- Reorder data sections via drag-and-drop
- Set section priority (Required/Optional)
- Preview final data structure

**Step 3: Prompt Engineering**
- Write prompt template with placeholders
- Monaco-style code editor with syntax highlighting
- Real-time validation of placeholders
- Preview final prompt with actual data

**Step 4: Model Testing**
- Select AI models (OpenAI, Anthropic, Google)
- Configure temperature and max tokens
- View cost estimates
- Generate news articles

**Step 5: Results & Comparison**
- View side-by-side outputs from different models
- Compare quality and cost
- Rate generated content
- View iteration history

**Final: Publishing**
- Review validation checklist
- See configuration summary
- View diff from current production
- Publish to production or save as draft

## 🎯 Key Features

### Smart Dropdown Selector
- Dropdown shows all triggers with status badges (Configured, In Progress, Unconfigured)
- Disabled state when no trigger selected
- Smooth transition to Configuration Workspace

### Monaco-Style Prompt Editor
- Syntax highlighting for placeholders `{{variable}}`
- Line numbers and minimap
- Real-time validation
- Auto-save indicator

### Multi-Model Testing
- Support for OpenAI (GPT-4, GPT-3.5), Anthropic (Claude 3), Google (Gemini)
- Configurable temperature and token limits
- Cost estimation before generation
- Side-by-side comparison of outputs

### Version Control
- Configuration history with version numbers
- Active production indicator
- Rollback capability
- Diff viewer for version comparison

### Publishing Workflow
- Pre-publish validation
- Warning for stale tests
- Configuration summary review
- Diff preview
- Safe publish with confirmation

## 🛠️ Technical Stack

- **React** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/ui** - Component library
- **Lucide React** - Icons
- **Bootstrap 5 Design System** - Color palette and spacing

## 📱 Responsive Design

- **Desktop Primary**: 1920x1080px (main viewport)
- **Desktop Secondary**: 1366x768px
- **Tablet**: Horizontal tab navigation replaces vertical sidebar
- **Mobile**: Show "Use desktop for best experience" message

## ♿ Accessibility

- Proper ARIA labels on all interactive elements
- Keyboard navigation support
- Focus indicators on all focusable elements
- Screen reader compatible
- WCAG AA color contrast compliance (4.5:1 minimum)

## 🎨 Design Tokens

### Buttons
- **Standard**: 40px height
- **Large**: 48px height
- **Small**: 36px height

### Inputs
- **Height**: 40px
- **Border**: 1px solid #ced4da
- **Border Radius**: 4px
- **Focus**: Blue border (#0d6efd)

### Cards & Panels
- **Border Radius**: 8px
- **Padding**: 24px
- **Shadow**: 0 2px 4px rgba(0,0,0,0.08)

### Modals
- **Max Width**: 700px (publish modal)
- **Border Radius**: 8px
- **Overlay**: rgba(0,0,0,0.6)

## 🔮 Future Enhancements (Post-MVP)

- **Audit Log**: System-wide activity tracking
- **Settings**: User preferences and profile management
- **User Management**: Role-based access control
- **Advanced Analytics**: Performance metrics and insights
- **Batch Operations**: Configure multiple triggers
- **Scheduled Publishing**: Time-based deployments
- **A/B Testing**: Compare different configurations
- **Custom Workflows**: Define custom approval processes

## 📝 Notes

- This is an **MVP (Minimum Viable Product)** focused on core workflow
- All components follow Bootstrap 5 design principles
- Dark navbar (#212529) with light content area (#f8f9fa)
- Consistent 8px spacing grid throughout
- All interactive elements have hover states
- Loading states use shimmer animation
- Error states use red color scheme (#dc3545)

## 🎓 Learning Resources

- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Shadcn/ui Components](https://ui.shadcn.com/)
- [Radix UI Primitives](https://www.radix-ui.com/)

---

**Version**: 2.2 (Backend Default Selections & Workflow)  
**Last Updated**: October 28, 2025  
**Design System**: Bootstrap 5  
**Status**: ✅ Production Ready

## 📝 Version History

### v2.2 (Current) - Backend Default Selections
- ✅ Data sections pre-selected by backend on page load (5 default sections)
- ✅ Button renamed: "Fetch Data" → "Use This Data" with arrow-right icon
- ✅ Status badge: "Default configuration" indicator for initial state
- ✅ Trigger Context Bar: Status badges (Configure Data, Data Ready, Configuration Error)
- ✅ Section Management: Dynamically shows only selected sections
- ✅ State management: Shared selectedSections between panels

### v2.1 - Multi-Select Dropdown
- Data Configuration with checkbox-based multi-select dropdown
- 14 hardcoded data sections
- "Select All" / "Clear All" functionality

### v2.0 - MVP Scope
- Dashboard with dropdown trigger selector
- Removed Audit Log and Settings screens
- Streamlined workflow focus
