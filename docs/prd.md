# AI-Powered News CMS for Equity Market Research Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Enable content managers to configure AI news generation workflows without developer dependency
- Reduce configuration time from days to hours (>90% reduction)
- Support rapid experimentation with prompts, data sources, and AI models
- Support multiple prompt types (paid, unpaid, crawler) for different content distribution channels
- Provide complete visibility into data APIs, structured data, and generation pipeline
- Create scalable foundation for managing 20+ news trigger categories with multi-type prompt variations
- Improve news quality through iterative testing and optimization across different content types
- Eliminate 80% of developer time spent on content configuration tasks
- Enable publishing of production-ready configurations with confidence through comprehensive testing

### Background Context

Our equity market research platform generates AI-powered news articles based on various triggers (earnings results, analyst grade changes, price movements, etc.), but the current system is rigid and hardcoded. Data APIs, prompts, and LLM models are embedded in scripts, requiring developer intervention for any changes. This creates significant friction: content teams cannot experiment with different approaches, iteration cycles are slow (days instead of hours), and there's no visibility into the actual data driving news generation. Additionally, the platform needs to support different content distribution channels (paid subscribers, unpaid users, web crawler/SEO content) with tailored prompts for each audience, but the current system cannot accommodate multiple prompt variations per trigger.

The News CMS will transform this process by providing a visual, interactive interface where content managers can select triggers, configure data sources, craft multiple prompt types (paid, unpaid, crawler) with real-time data preview, test multiple AI models side-by-side, iterate rapidly, and publish production configurations—all without writing code. This empowers content teams to optimize news generation strategies for different audiences, dramatically accelerates iteration cycles, and creates a scalable foundation for future growth.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-11-04 | 1.2 | Updated completion status for Stories 1.1-1.4, 2.1, 2.3, 2.5, 3.1-3.4, 3.4b | Claude |
| 2025-11-04 | 1.1 | Added Story 3.4b: Version Selection in Preview (completed) | Claude |
| 2025-10-24 | 1.0 | Initial PRD created from project brief | John (PM Agent) |

## Requirements

### Functional

- **FR1**: The system shall display a list of available news triggers/categories and allow users to select a trigger to configure
- **FR2**: The system shall accept stock ID input for testing and configuration purposes
- **FR3**: The system shall load existing configurations for a selected trigger, displaying current model, data APIs, and all three prompt types (paid, unpaid, crawler)
- **FR4**: The system shall display a list of data APIs currently configured for a trigger and allow users to add or remove APIs from a predefined list
- **FR5**: The system shall validate that required APIs are present in the configuration before allowing generation
- **FR6**: The system shall fetch data from configured APIs for a specified stock ID and display raw JSON responses in an organized, readable format
- **FR7**: The system shall show API call status indicators (success, failure, latency) for each data retrieval operation
- **FR8**: The system shall execute existing parser scripts to convert raw JSON data into structured format
- **FR9**: The system shall display structured data output with clear section labels and show the mapping between raw data and structured sections
- **FR10**: The system shall handle parser errors gracefully with clear, actionable error messages
- **FR11**: The system shall allow users to SELECT data sections in Data Configuration step (with checkboxes) and REORDER selected sections in Section Management step (using drag-and-drop)
- **FR12**: The system shall preview selected sections in Data Configuration and show section order in Section Management with ability to preview final data structure passed to AI models
- **FR13**: The system shall provide a tabbed full-text prompt editor with syntax highlighting and real-time validation of data placeholder references for each prompt type (paid, unpaid, crawler)
- **FR14**: The system shall display the current prompt template for the selected tab with clear indication of data placeholders
- **FR15**: The system shall preview the final prompt with actual data substituted before generation for the selected prompt type
- **FR16**: The system shall provide version history and undo capability for prompt changes per prompt type
- **FR17**: The system shall display available LLM models and allow selection of multiple models for parallel testing
- **FR18**: The system shall display model-specific settings (temperature, max tokens) and show cost estimates for selected models
- **FR19**: The system shall generate news articles in parallel across selected models for checked prompt types only when triggered by user
- **FR20**: The system shall display real-time generation status indicators during news creation per prompt type
- **FR21**: The system shall display generated news grouped by prompt type, then by model for comparison
- **FR22**: The system shall show generation metadata including time, tokens used, and actual cost for each generation per prompt type per model
- **FR23**: The system shall allow inline editing of data or prompts after initial generation and support rapid regeneration for selected prompt types
- **FR24**: The system shall track generation history within a session and indicate what changed between iterations including which prompt types were tested
- **FR25**: The system shall provide a "Publish" function to save finalized configurations for all three prompt types with confirmation dialog showing what will be saved
- **FR26**: The system shall validate that all prompt type configurations are complete and tested before allowing publication
- **FR27**: The system shall save published configurations including all three prompt types to database with versioning
- **FR28**: The system shall set published configurations for all prompt types as active for automated news generation in production
- **FR29**: The system shall validate that stock IDs exist in the database before processing
- **FR30**: The system shall handle API failures gracefully (timeout, rate limits, invalid responses) with user-friendly error messages
- **FR31**: The system shall prevent publishing of incomplete or untested configurations
- **FR32**: The system shall log all configuration changes with user identity, timestamp, and change details
- **FR33**: The system shall track which configurations are currently live in production
- **FR34**: The system shall maintain history of prompt versions and model selections for audit purposes
- **FR35**: The system shall support three independent prompt types (paid, unpaid, crawler) per trigger with separate prompt templates
- **FR36**: The system shall display paid prompt type by default with checkboxes to enable unpaid and crawler prompt types
- **FR37**: The system shall share data configuration (fetch/generate + section selection), section management (ordering), and model selection across all prompt types - selection happens in Data Configuration, ordering happens in Section Management
- **FR38**: The system shall provide a tabbed interface for editing prompts, allowing users to switch between paid, unpaid, and crawler prompt types
- **FR39**: The system shall generate news only for checked/selected prompt types
- **FR40**: The system shall display actual token usage, generation time, and cost per model per prompt type after generation completes

### Non Functional

- **NFR1**: The system shall load pages in under 2 seconds for optimal user experience
- **NFR2**: Data API fetching shall complete within 5 seconds per API call
- **NFR3**: News generation responses shall be delivered within 30 seconds (model dependent)
- **NFR4**: The system shall support 5-10 concurrent user sessions without degradation
- **NFR5**: The system shall be compatible with modern browsers (Chrome, Firefox, Safari, Edge) - last 2 versions
- **NFR6**: The system shall provide a responsive design optimized for desktop with tablet support
- **NFR7**: The system shall securely store API keys for LLM services with encryption
- **NFR8**: The system shall implement input validation to prevent injection attacks
- **NFR9**: The system shall implement rate limiting to prevent abuse and control costs
- **NFR10**: The system shall track LLM API costs and implement spending limits to prevent budget overruns
- **NFR11**: The system shall maintain backwards compatibility with existing news generation system during transition
- **NFR12**: The system shall respect LLM API rate limits and quotas
- **NFR13**: Published configurations shall generate production-quality news with less than 5% error rate
- **NFR14**: The system shall enable configuration creation from trigger selection to publication in under 2 hours
- **NFR15**: The system shall maintain comprehensive audit logs for compliance purposes

## User Interface Design Goals

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
   - Data Configuration panel (fetch/generate data, SELECT sections with checkboxes, "Use This Data" button to proceed)
   - Section Management panel (REORDER selected sections using drag-and-drop, OLD section + NEW sections in OLD_NEW mode)
   - Prompt editor (syntax highlighting, placeholder validation, preview, tabbed for paid/unpaid/crawler)
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

## Technical Assumptions

### Repository Structure: Monorepo

**Decision**: Use a **Monorepo** structure with separate packages for frontend, backend, and shared Python/TypeScript types.

**Rationale**:
- **Shared Code**: Frontend and backend need to share configuration schemas and data models—monorepo enables single source of truth
- **Coordinated Changes**: Features often span both frontend and backend (e.g., adding a new LLM model requires API changes + UI updates)—monorepo allows atomic commits
- **Simplified Development**: Unified version control, easier local development setup
- **Internal Tool Scale**: This is not a distributed system with independent deployment cycles; tight coupling is acceptable

**Structure**:
```
news-cms/
├── frontend/              # Next.js/React application
├── backend/               # Python/FastAPI application
├── shared/                # Shared schemas and types
├── scripts/               # Deployment and utility scripts
└── README.md
```

### Service Architecture

**Architecture**: **Monolithic Application (No Microservices, No Containerization)**

**Core Components**:

1. **CMS API Service** (Backend Layer - Python/FastAPI)
   - Handles all CMS operations: trigger management, configuration CRUD, user sessions
   - RESTful API design with clear versioning
   - Executes existing parser scripts directly (assumes Python parsers)
   - Calls LLM APIs for news generation (synchronous for MVP, can be async with background tasks)
   - **Technology**: Python 3.11+ with FastAPI + Pydantic for validation

2. **Data Integration Layer**
   - Adapter pattern for existing data APIs
   - Handles authentication, rate limiting, error retry logic
   - In-memory caching for frequently accessed data (can use Python functools.lru_cache or similar)
   - **Technology**: Part of FastAPI backend, isolated modules for each data source

3. **LLM Gateway/Abstraction**
   - Unified interface for OpenAI, Anthropic, Google AI
   - Cost tracking and rate limiting per provider
   - Request/response logging for audit
   - **Technology**: Python abstraction layer within FastAPI backend

**Rationale**:
- **Monolithic Architecture**: Simpler deployment, easier debugging, appropriate for internal tool with limited scale (5-10 concurrent users)
- **No Containerization**: Reduces infrastructure complexity; direct deployment to AWS EC2 or Elastic Beanstalk
- **Python Backend**: Aligns with existing parser scripts (assumption: parsers are Python-based), strong ecosystem for data processing and LLM integrations
- **Synchronous Processing for MVP**: News generation within 30-second timeout can be handled synchronously; async background jobs can be added post-MVP if needed using FastAPI BackgroundTasks or Celery

### Testing Requirements

**Testing Strategy**: **Unit + Integration with Manual E2E for MVP**

**Required Testing**:

1. **Unit Tests**
   - **Frontend**: Component tests for UI interactions (React Testing Library, Jest)
   - **Backend**: API endpoint tests, business logic tests (pytest)
   - **Coverage Target**: 70%+ for critical paths (configuration validation, publish logic, API integration)

2. **Integration Tests**
   - **API Contract Tests**: Validate frontend-backend communication with real HTTP calls
   - **Data Integration Tests**: Test adapter layer against mock/sandbox data APIs
   - **Parser Integration Tests**: Validate existing parser script execution
   - **LLM Integration Tests**: Mock LLM responses for cost control, occasional real API tests in staging

3. **Manual E2E Testing** (for MVP)
   - **Rationale**: Full E2E automation adds significant development time; manual testing sufficient for internal tool with small user base
   - **Test Cases**: Document critical user flows (trigger setup → generate → publish) for manual QA before releases
   - **Post-MVP**: Automate most common happy paths and critical edge cases

4. **Load/Performance Testing**
   - Simple load tests for concurrent user sessions (5-10 users)
   - LLM API timeout and rate limit simulation

**Testing Convenience Requirements**:
- **Seed Data**: Python scripts to populate MongoDB with sample triggers, configurations, and historical data
- **Mock Mode**: Ability to run CMS with mock LLM responses for cost-free testing
- **Parser Stubs**: Mock parser outputs for frontend development without backend dependencies

**Rationale**:
- **pytest for Python**: Industry standard, excellent fixtures and mocking capabilities
- **Manual E2E**: Acceptable trade-off given internal tool, small user base, and controlled rollout
- **Parser Integration Risk**: Existing parsers are external dependencies; thorough integration testing is critical

### Additional Technical Assumptions and Requests

**Frontend Technology Stack**:
- **Framework**: Next.js (App Router) with TypeScript
  - **Rationale**: Server-side rendering for initial load performance, excellent developer experience, modern React patterns
- **UI Library**: Bootstrap 5
  - **Rationale**: Lightweight, widely known, excellent responsive grid system, no heavy build-time dependencies
  - **Implementation**: React-Bootstrap for React components
- **Prompt Editor**: Monaco Editor
  - **Rationale**: Same editor as VS Code, excellent syntax highlighting, built-in diff view for prompt comparison
- **State Management**: React Context API
  - **Rationale**: Built-in to React, no additional dependencies, sufficient for MVP scope, eliminates external state management library overhead
  - **Pattern**: Separate contexts for user session, configuration state, and generation results
- **HTTP Client**: Axios or Fetch API
  - **Rationale**: Simple REST API communication with FastAPI backend
- **Real-time Updates**: Polling or Server-Sent Events (SSE) for generation status updates
  - **Rationale**: Simpler than WebSockets for one-way server→client updates, FastAPI has native SSE support

**Backend Technology Stack**:
- **Runtime**: Python 3.11+ with FastAPI
  - **Rationale**: Aligns with existing parser scripts (assumed Python), excellent async support, automatic OpenAPI documentation, Pydantic validation
- **Validation**: Pydantic v2
  - **Rationale**: Built into FastAPI, runtime validation + type hints, use for configuration schemas and API models
- **Parser Integration**: Direct Python module imports or subprocess calls
  - **Rationale**: If parsers are Python modules, import directly; if standalone scripts, use subprocess with proper error handling
- **LLM Client Libraries**:
  - OpenAI: `openai` Python package
  - Anthropic: `anthropic` Python package
  - Google: `google-generativeai` Python package
- **Authentication**: Cookie-based authentication
  - **Rationale**: Integrates with existing authentication system, no separate login page needed

**Database**:
- **Database**: MongoDB Community Edition
  - **Rationale**: Flexible schema for diverse configuration structures, excellent for storing JSON-like data (API responses, prompts), simple setup without licensing costs
  - **Driver**: Motor (async MongoDB driver for Python) or PyMongo (sync driver)
  - **Collections**: triggers, configurations, prompts (versioned), generation_history, audit_log
  - **Schema Design**: Use Pydantic models to enforce schema validation at application layer

**Configuration Schema for Multi-Type Prompts**:
```javascript
Configuration {
  _id: ObjectId,
  trigger_id: string,
  version: number,

  // SHARED across all prompt types
  data_sections: [string],              // Selected data section IDs
  section_order: [string],              // Order of sections in data structure
  model_config: {                       // Applies to all prompt types
    selected_models: [string],          // e.g., ["gpt-4", "claude-3-sonnet"]
    temperature: number,
    max_tokens: number
  },

  // SEPARATE per prompt type
  prompts: {
    paid: {
      template: string,                 // Prompt template with placeholders
      version_history: [{
        template: string,
        timestamp: datetime,
        user_id: string
      }],
      last_test_generation: {
        timestamp: datetime,
        stock_id: string,
        results: []
      }
    },
    unpaid: {
      template: string,
      version_history: [],
      last_test_generation: {}
    },
    crawler: {
      template: string,
      version_history: [],
      last_test_generation: {}
    }
  },

  // Metadata
  created_by: string,
  created_at: datetime,
  updated_at: datetime,
  published_at: datetime,
  is_active: boolean                    // True if this is the production version
}
```

**AWS Infrastructure** (No Containerization):
- **Application Hosting**:
  - **Backend**: AWS EC2 instance (t3.medium or similar) or AWS Elastic Beanstalk for Python
  - **Frontend**: Build static Next.js export and serve from S3 + CloudFront OR deploy Next.js app to same EC2 instance with Nginx reverse proxy
- **Database**: MongoDB Community Edition on dedicated EC2 instance OR MongoDB Atlas (managed service)
- **Storage**: S3 for logs, configuration backups, and static assets
- **Secrets Management**: AWS Secrets Manager for LLM API keys and database credentials
- **Deployment**:
  - EC2 with systemd service for FastAPI backend (using uvicorn)
  - Nginx as reverse proxy for SSL termination and routing
  - No Docker—direct Python virtual environment deployment
- **CI/CD**: GitHub Actions or AWS CodePipeline
  - **Pipeline**: Lint → Test → Build → Deploy to staging EC2 → Manual approval → Deploy to production EC2
- **Environments**: Development (local), Staging (AWS EC2), Production (AWS EC2)

**Integration with Existing Systems**:
- **Data APIs**: Assume RESTful JSON APIs with API key authentication
  - FastAPI adapter modules handle API calls using `httpx` or `requests`
- **Parser Scripts**: Assume Python scripts/modules that accept JSON input and return structured output
  - Direct import or subprocess execution from FastAPI backend
- **Publication Pipeline**: Published configurations stored in MongoDB; existing news generation system reads from same database
  - **Alternative**: Expose REST API endpoint for existing system to fetch active configurations

**Security & Authentication**:
- **API Authentication**: Cookie-based authentication for API requests
  - No separate login page required (assumes integration with existing authentication system)
- **API Security**: LLM API keys stored in AWS Secrets Manager, fetched at application startup
- **HTTPS**: SSL/TLS certificates managed via AWS Certificate Manager + Nginx
- **Input Validation**: All user inputs validated to prevent injection attacks

**Logging & Monitoring**:
- **Application Logs**: Python logging module with structured JSON output
- **Log Storage**: CloudWatch Logs or S3
- **Monitoring**: AWS CloudWatch for basic metrics (CPU, memory, request counts)
- **Error Tracking**: Optional: Sentry for error monitoring

**Data Retention & Audit**:
- **Configuration History**: Retain all versions indefinitely in MongoDB (use versioning pattern)
- **Generation History**: Retain test generations for 30 days, production generations indefinitely
- **Audit Logs**: Retain all user actions indefinitely for compliance (separate MongoDB collection)

## Epic List

**Epic 1: Foundation & Core Infrastructure**
Establish project setup, authentication, database connectivity, and basic UI framework while delivering initial trigger management functionality.

**Epic 2: Data Pipeline & Integration**
Build the data retrieval and transformation pipeline, enabling users to configure APIs, fetch stock data, execute parsers, and preview structured data.

**Epic 3: Prompt Engineering Workspace**
Create the prompt editing environment with real-time data substitution, section management, and preview capabilities.

**Epic 4: Multi-Model Generation & Testing**
Implement LLM integration, parallel model testing, side-by-side comparison, and iterative refinement workflow.

**Epic 5: Configuration Publishing & Production Integration**
Enable publishing of tested configurations to production with validation, audit trails, and integration with existing news generation system.

## Epic 1: Foundation & Core Infrastructure

**Goal**: Establish the technical foundation for the News CMS including project structure, core infrastructure (FastAPI backend, Next.js frontend, MongoDB database), basic UI shell, and trigger management. This epic delivers a deployable "walking skeleton" that allows users to view and select news triggers—providing immediate value while establishing the architecture for all subsequent features. Authentication is handled via cookies from the existing authentication system.

### Story 1.1: Project Setup and Monorepo Structure ✅ COMPLETED

**As a** developer,
**I want** a properly configured monorepo with frontend and backend projects,
**so that** the team can develop both applications with consistent tooling and shared dependencies.

**Acceptance Criteria**:
1. ✅ Monorepo created with `frontend/` (Next.js + TypeScript) and `backend/` (Python/FastAPI) directories
2. ✅ Frontend package.json configured with Next.js 14+, TypeScript, React-Bootstrap, and Monaco Editor dependencies
3. ✅ Backend pyproject.toml or requirements.txt configured with FastAPI, Pydantic v2, Motor (MongoDB async driver), and pytest
4. ✅ Shared schemas directory created with example Pydantic model exported for use by both frontend and backend
5. ✅ Root-level README.md documents project structure, local development setup instructions, and technology stack
6. ✅ Git repository initialized with appropriate .gitignore files for Node.js and Python
7. ✅ Both frontend and backend applications start successfully in local development mode (npm run dev, uvicorn)

### Story 1.2: MongoDB Database Setup and Connection ✅ COMPLETED

**As a** developer,
**I want** MongoDB database connectivity configured with initial collections,
**so that** the application can persist triggers, configurations, and audit data.

**Acceptance Criteria**:
1. ✅ MongoDB Community Edition installed locally or MongoDB Atlas connection configured
2. ✅ Pydantic models created for core collections: Trigger, Configuration, User, AuditLog
3. ✅ FastAPI backend establishes async connection to MongoDB using Motor driver on startup
4. ✅ Database connection health check endpoint `/api/health` returns MongoDB connection status
5. ✅ Migration script (or documentation) creates initial collections with appropriate indexes (e.g., trigger_id, user_id, created_at)
6. ✅ Sample seed data script populates database with 3-5 example triggers for development testing
7. ✅ Environment variable configuration for MongoDB connection string (supports local and cloud deployments)
8. ✅ Graceful error handling and logging if MongoDB connection fails

### Story 1.3: Basic UI Shell and Navigation ✅ COMPLETED

**As a** content manager,
**I want** a professional, navigable UI shell with Bootstrap styling,
**so that** I can access different areas of the CMS intuitively.

**Acceptance Criteria**:
1. ✅ Next.js App Router layout created with Bootstrap 5 CSS imported globally
2. ✅ Responsive navigation bar using React-Bootstrap Navbar component with logo placeholder
3. ✅ Navigation includes links to: Dashboard (Triggers), Configuration Workspace (disabled until trigger selected), Settings (placeholder)
4. ✅ Footer displays application name and version
5. ✅ Application meets NFR6: Responsive design with 1200px+ desktop layout and 768px+ tablet layout
6. ✅ All pages use consistent Bootstrap grid system and spacing utilities
7. ✅ Basic loading spinner component created for future async operations

### Story 1.4: Trigger Management Dashboard ✅ COMPLETED

**As a** content manager,
**I want** to view a list of available news triggers with status information,
**so that** I can select a trigger to configure.

**Acceptance Criteria**:
1. ✅ FastAPI endpoint `GET /api/triggers` returns list of all triggers from MongoDB (name, description, status, last_updated)
2. ✅ Frontend Dashboard page fetches and displays triggers in Bootstrap Table or Card grid
3. ✅ Each trigger shows: name, description, configuration status (Configured/Unconfigured), last updated timestamp
4. ✅ Visual status indicator (badge or icon) distinguishes configured vs. unconfigured triggers
5. ✅ Clicking a trigger navigates to Configuration Workspace with trigger ID in URL (`/config/:triggerId`)
6. ✅ Empty state displayed if no triggers exist (with message suggesting database seeding)
7. ✅ Loading state displayed while fetching triggers from API
8. ✅ Error handling displays user-friendly message if API call fails
9. ✅ Meets NFR1: Page loads in under 2 seconds with 10+ triggers

### Story 1.5: AWS Deployment Setup for Staging Environment

**As a** developer,
**I want** the application deployed to AWS EC2 staging environment,
**so that** stakeholders can test the foundation in a production-like setting.

**Acceptance Criteria**:
1. AWS EC2 instance (t3.medium) provisioned for staging environment
2. MongoDB installed and running on dedicated EC2 instance or MongoDB Atlas configured
3. Python 3.11+ installed with FastAPI backend deployed using virtual environment
4. FastAPI backend runs as systemd service using uvicorn (auto-restart on failure)
5. Next.js frontend build deployed (either static export to S3+CloudFront or running on same EC2 with Node.js)
6. Nginx configured as reverse proxy for SSL termination and routing (frontend, backend API)
7. SSL certificate configured using AWS Certificate Manager (HTTPS enabled)
8. AWS Secrets Manager stores MongoDB credentials and LLM API keys
9. Basic CI/CD pipeline (GitHub Actions) deploys to staging on push to `develop` branch
10. Staging environment accessible via public URL (e.g., https://staging.news-cms.example.com)
11. CloudWatch Logs configured to capture application logs (FastAPI and Next.js)
12. Health check endpoint `/api/health` accessible and returns 200 status

## Epic 2: Data Pipeline & Integration

**Goal**: Build the complete data retrieval and transformation pipeline that connects to external data APIs, executes parser scripts, and displays structured data. This epic enables content managers to configure which data sources feed into news generation and preview the actual data that will be used in prompts—addressing the critical pain point of "no visibility into data." **Note**: Data configuration is shared across all three prompt types (paid, unpaid, crawler) for consistency and efficiency.

### Story 2.1: API Configuration Interface ✅ COMPLETED

**As a** content manager,
**I want** to add and remove data APIs from a trigger's configuration,
**so that** I can control which data sources are used for news generation.

**Acceptance Criteria**:
1. ✅ Configuration Workspace page loads trigger details from `GET /api/triggers/:id/config` (includes currently configured APIs)
2. ✅ "Data Sources" panel displays list of currently configured APIs with remove button for each
3. ✅ "Add API" dropdown or modal shows predefined list of available data APIs (from backend registry or database)
4. ✅ Clicking "Add API" sends `POST /api/triggers/:id/config/apis` with API identifier, updates UI optimistically
5. ✅ Clicking "Remove" button sends `DELETE /api/triggers/:id/config/apis/:apiId`, updates UI
6. ✅ Backend validates that required APIs are present before allowing removal (FR5)
7. ✅ Changes auto-save to MongoDB Configuration collection
8. ✅ Toast notification confirms successful add/remove operations
9. ✅ Error handling prevents adding duplicate APIs and displays clear error message

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

### Story 2.3: Data Retrieval and Raw JSON Display ✅ COMPLETED

**As a** content manager,
**I want** to fetch and view raw JSON data from configured APIs for a specific stock,
**so that** I understand exactly what data is being retrieved.

**Acceptance Criteria**:
1. ✅ Configuration Workspace includes stock ID input field with "Fetch Data" button
2. ✅ Backend endpoint `POST /api/triggers/:id/data/fetch` accepts stock ID and returns raw JSON from all configured APIs
3. ✅ Frontend displays loading indicator during data fetch (meets NFR2: completes within 5 seconds per API)
4. ✅ Raw JSON displayed in collapsible panels (one per API) with syntax highlighting (JSON formatting)
5. ✅ Each API panel shows: API name, fetch status (success/failure), latency, timestamp
6. ✅ Failed API calls display error message (timeout, 404, 500) without blocking other APIs
7. ✅ Success state shows formatted JSON with expand/collapse capability for nested objects
8. ✅ "Refresh Data" button allows re-fetching without re-entering stock ID
9. ✅ Stock ID validation checks format before allowing fetch (prevents invalid requests)
10. ✅ Meets FR6 and FR7: organized display with status indicators

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

### Story 2.5: Structured Data Display and Section Preview ✅ COMPLETED

**As a** content manager,
**I want** to view the structured data output from parsers with clear section labels,
**so that** I can verify the data is correctly organized before writing prompts.

**Acceptance Criteria**:
1. ✅ After parsing, "Structured Data" panel displays sections returned by parser
2. ✅ Each section displayed in separate Bootstrap Card with section name as header
3. ✅ Section content formatted appropriately (paragraphs, bullet lists, tables based on data structure)
4. ✅ Collapsible sections allow focusing on specific data areas
5. ✅ Visual mapping indicator shows which raw API data contributed to each section (e.g., "Source: Earnings API")
6. ✅ Sections numbered or labeled to support referencing in prompts
7. ✅ Empty sections (no data available) display placeholder message rather than blank space
8. ✅ "Preview Final Data Structure" button shows JSON representation of complete structured data as it will be passed to LLM
9. ✅ Meets FR9: clear section labels and mapping between raw and structured data
10. ✅ Data persists in UI state (React Context) for use in prompt editing without re-fetching

## Epic 3: Prompt Engineering Workspace

**Goal**: Create the prompt editing environment where content managers craft and refine prompts using real data. This epic delivers the core creative workspace with section management, tabbed prompt editor for multiple types (paid, unpaid, crawler), syntax-highlighted editing, real-time validation, and preview capabilities—enabling rapid prompt iteration without developer dependency. **Note**: Section management is shared across all prompt types, but each type has its own independent prompt template accessible via tabs.

**Stories**: ✅ 3.1 (COMPLETED), ✅ 3.2 (COMPLETED), ✅ 3.3 (COMPLETED), ✅ 3.4 (COMPLETED), ✅ 3.4b (COMPLETED 2025-11-04), 3.5 (In Progress)

**Status**: Stories 3.1-3.4b completed - full prompt workspace with section reordering, Monaco editor integration with syntax highlighting and validation, preview with data substitution, and version selection. Story 3.5 (Version History UI) partially complete (backend done, frontend UI pending).

### Story 3.1: Section Reordering Interface (Shared Across All Prompt Types) ✅ COMPLETED

**As a** content manager,
**I want** to reorder data sections via drag-and-drop or numbered input,
**so that** I can control the sequence in which data appears in all prompt types (paid, unpaid, crawler).

**Acceptance Criteria**:
1. ✅ "Section Order" panel displays structured data sections in current order
2. ✅ Drag-and-drop functionality implemented using React DnD library or Bootstrap Sortable
3. ✅ Alternative numbered input allows typing new position (e.g., move section 3 to position 1)
4. ✅ Section order changes immediately reflected in UI without page reload
5. ✅ "Preview Data Structure" updates to show new section order in final JSON
6. ✅ Section order saved to Configuration in MongoDB when changed (auto-save or explicit save button)
7. ✅ Meets FR11 and FR12: reordering capability with preview of effects
8. ✅ Undo/redo support for section order changes (single-level undo sufficient for MVP)
9. ✅ Visual feedback during drag operation (highlighting drop zones)

### Story 3.2: Tabbed Prompt Editor with Syntax Highlighting ✅ COMPLETED

**As a** content manager,
**I want** a tabbed full-featured text editor for crafting prompts for each type (paid, unpaid, crawler) with syntax highlighting,
**so that** I can write complex prompts comfortably for different audiences and see placeholder references clearly.

**Acceptance Criteria**:
1. ✅ Monaco Editor component integrated into Configuration Workspace with tabbed interface
2. ✅ Tabs displayed horizontally: [Paid] [Unpaid] [Crawler] - showing only checked prompt types from Trigger Context Bar
3. ✅ Active tab highlighted with blue underline, inactive tabs shown in gray
4. ✅ Clicking a tab switches the editor content to that prompt type's template
5. ✅ Each prompt type maintains its own template, independent of other types
6. ✅ Prompt editor displays current prompt template for selected tab or blank template for new configurations
7. ✅ Syntax highlighting configured for prompt format (highlighting placeholders like `{{section_name}}` or `{data.field}`)
8. ✅ Line numbers, search/replace, and keyboard shortcuts (Ctrl+F, Ctrl+Z) available
9. ✅ Editor resizable or full-screen mode for extended editing sessions
10. ✅ Meets FR13, FR14, FR38: tabbed editor with syntax highlighting for multiple prompt types
11. ✅ Auto-save prompt changes to React Context every 5 seconds (debounced) per prompt type
12. ✅ Editor theme configurable (light/dark mode) based on user preference or system setting
13. ✅ Word count or character count displayed per prompt type (helpful for LLM token estimation)
14. ✅ Tab icons: 💰 Paid, 🆓 Unpaid, 🕷️ Crawler for visual clarity

### Story 3.3: Data Placeholder Validation (Per Prompt Type) ✅ COMPLETED

**As a** content manager,
**I want** real-time validation of data placeholders in my prompt for the selected tab,
**so that** I catch errors before generation and know which data fields are available for each prompt type.

**Acceptance Criteria**:
1. ✅ Prompt editor parses placeholders in real-time for the currently active tab (e.g., `{{section_name}}`, `{data.field}`)
2. ✅ Invalid placeholders (referencing non-existent sections or fields) underlined in red with hover tooltip error message
3. ✅ Valid placeholders show green checkmark or no error indicator
4. ✅ Autocomplete suggestions appear when typing `{{` showing available section names and fields (same for all types since data is shared)
5. ✅ Validation runs on every keystroke (debounced to avoid performance issues) for active tab only
6. ✅ Validation error summary panel displays list of all invalid placeholders found in current tab's prompt
7. ✅ Clicking error in summary highlights corresponding placeholder in editor
8. ✅ Meets FR13: real-time validation of placeholder references per prompt type
9. ✅ Helper documentation or info icon explains placeholder syntax and available data fields
10. ✅ Tab indicator shows validation status (warning icon if errors exist in that tab's prompt)

### Story 3.4: Prompt Preview with Data Substitution (Per Prompt Type) ✅ COMPLETED

**As a** content manager,
**I want** to preview my prompt with actual data substituted for placeholders for the selected prompt type,
**so that** I can see exactly what will be sent to the LLM before generating.

**Acceptance Criteria**:
1. ✅ "Preview Prompt" button triggers substitution of placeholders with actual structured data for currently active tab
2. ✅ Preview displayed in read-only panel (Bootstrap Card or Modal) showing final prompt text for selected prompt type
3. ✅ Placeholders replaced with real values from current structured data state (shared across all types)
4. ✅ Sections included in order defined by section reordering (shared across all types)
5. ✅ Missing data (placeholder references non-existent value) shown with placeholder in red or warning marker
6. ✅ Preview updates automatically when data, section order, or tab selection changes
7. ✅ Meets FR15: preview of final prompt with actual data substituted per prompt type
8. ✅ Preview displays estimated token count for LLM (approximate calculation based on character count)
9. ✅ "Copy to Clipboard" button allows copying previewed prompt for external testing
10. ✅ Preview includes metadata: stock ID, trigger name, prompt type (paid/unpaid/crawler), timestamp
11. ✅ Modal shows tabs to preview all checked prompt types if desired

### Story 3.4b: Prompt Version Selection in Preview ✅ COMPLETED (2025-11-04)

**As a** content manager,
**I want** to view and compare different saved versions of my prompts in the preview modal,
**so that** I can see how prompts evolved over time and ensure I'm reviewing the correct version.

**Acceptance Criteria**:
1. ✅ Version dropdown added to preview modal header showing all saved versions
2. ✅ "Current (Unsaved)" option displays latest editor content with unsaved changes
3. ✅ Historical version options labeled with version number, timestamp, and author (e.g., "v3 - Nov 4, 2:30 PM by user123")
4. ✅ Selecting a version fetches complete prompt data from backend via GET /api/triggers/:id/config/prompts/version/:version
5. ✅ Preview updates to show selected version's prompts with data substitution
6. ✅ Version badge indicates current viewing mode (yellow "Unsaved" for current, blue "v{number}" for saved)
7. ✅ Smooth version switching without flickering or multiple "Generating..." flashes
8. ✅ Backend endpoints implemented: GET /api/triggers/:id/config/prompts/versions (list all), GET /api/triggers/:id/config/prompts/version/:version (fetch specific)
9. ✅ Version history automatically loaded when preview modal opens
10. ✅ Version dropdown disabled during loading/generation to prevent conflicts
11. ✅ Modal resets to "Current" version when closed to avoid confusion on next open

**Technical Implementation**:
- Backend: Two new endpoints in triggers.py for version listing and retrieval
- Frontend: PreviewContext enhanced with version state management (selectedVersion, versionHistory, loadVersionHistory, loadVersionPreview)
- Frontend: PreviewModal updated with version selector UI component
- Database: Queries trigger_prompt_drafts collection, sorted by version/timestamp
- State Management: Proper dependency arrays to prevent circular re-renders

**Files Modified**:
- backend/app/routers/triggers.py (lines 573-696)
- backend/app/models/trigger_prompt_draft.py (schema with nested prompts)
- frontend/src/contexts/PreviewContext.tsx (version state & fetch functions)
- frontend/src/components/config/PreviewModal.tsx (version selector UI)
- frontend/src/types/preview.ts (VersionHistoryItem, VersionResponse, VersionData interfaces)

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

## Epic 4: Multi-Model Generation & Testing

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

## Epic 5: Configuration Publishing & Production Integration

**Goal**: Enable content managers to confidently publish tested configurations to production with validation safeguards, versioning, comprehensive audit trails, and integration with the existing news generation system. This epic closes the loop from testing to production deployment, delivering the key business value of eliminating developer dependency.

### Story 5.1: Pre-Publish Validation (All Prompt Types)

**As a** content manager,
**I want** the system to validate all prompt type configurations before publishing,
**so that** I don't accidentally deploy incomplete or untested configurations for any audience type.

**Acceptance Criteria**:
1. "Publish" button triggers validation checks for all three prompt types before allowing publication
2. Validation rules implemented per prompt type: prompt not empty, at least one successful test generation exists for each type
3. Shared validation: at least one API configured (FR5), section order defined, model selected
4. Validation failure displays modal with checklist of issues grouped by prompt type and prevents publishing
5. Validation success enables "Confirm Publish" button
6. Meets FR26 and FR31: validation of complete and tested configurations for all prompt types before publish
7. Visual checklist shows:
   - ✓ APIs configured (shared)
   - ✓ Section order defined (shared)
   - ✓ Model selected (shared)
   - Per prompt type:
     - ✓ Paid prompt created and tested
     - ✓ Unpaid prompt created and tested
     - ✓ Crawler prompt created and tested
8. Warning if any prompt type configuration differs from last successful test (prompt changed without re-testing)
9. Optional: Suggest minimum testing threshold (e.g., "Test all prompt types with at least 2 models before publishing")
10. Validation errors include actionable guidance per prompt type (e.g., "Paid prompt is empty - add prompt content to continue")

### Story 5.2: Configuration Publishing with Confirmation (All Prompt Types)

**As a** content manager,
**I want** to review and confirm exactly what will be published for all prompt types,
**so that** I understand what changes are going live in production for each audience type.

**Acceptance Criteria**:
1. After validation, "Confirm Publish" button opens confirmation modal showing what will be saved for all three prompt types
2. Confirmation modal displays:
   - Trigger name
   - Configured APIs (list) - shared
   - Section order - shared
   - Selected model and settings - shared
   - Per prompt type:
     - 💰 Paid prompt (truncated preview with character count)
     - 🆓 Unpaid prompt (truncated preview with character count)
     - 🕷️ Crawler prompt (truncated preview with character count)
3. Diff view if updating existing configuration (shows what changed from current production version for each prompt type)
4. Expandable sections per prompt type to view full prompt in modal
5. "Publish to Production" final button in modal triggers backend `POST /api/triggers/:id/publish` with all three prompt types
6. Backend saves configuration to MongoDB with version number (auto-incrementing) including all prompt types
7. Published configuration marked as "active" for the trigger (only one active config per trigger, contains all three prompt types)
8. Meets FR25, FR27, FR28: publish function with confirmation, versioning, and activation for all prompt types
9. Success notification displays version number, timestamp, and summary: "Published configuration with 3 prompt types"
10. Published configuration immediately available for use by automated news generation system for all prompt types
11. "View Published Configuration" link navigates to read-only view of active production config showing all three prompt types

### Story 5.3: Audit Logging and Change Tracking

**As a** compliance officer or system administrator,
**I want** comprehensive audit logs of all configuration changes,
**so that** we can track who made changes, when, and what was changed.

**Acceptance Criteria**:
1. All configuration changes logged to MongoDB `audit_log` collection with: user_id, action, timestamp, trigger_id, details (JSON diff)
2. Logged actions include: configuration created, updated, published, API added/removed, prompt edited, model changed
3. Backend middleware automatically logs all write operations to configurations
4. Meets FR32, FR33, FR34: logging of changes, tracking production configs, maintaining history
5. Audit log UI accessible from navigation (admin/audit page)
6. Audit log table displays: timestamp, user, trigger, action, details (expandable)
7. Filtering by trigger, user, date range, action type
8. Export audit log to CSV or JSON for compliance reporting
9. Audit logs immutable (no deletion or editing allowed via UI)
10. Meets NFR15: comprehensive audit logs for compliance

### Story 5.4: Configuration Version History and Rollback

**As a** content manager,
**I want** to view previous configuration versions and rollback if needed,
**so that** I can recover from mistakes or compare historical approaches.

**Acceptance Criteria**:
1. "Configuration History" screen accessible from Configuration Workspace
2. History displays all published versions for selected trigger with version number, timestamp, published by (user)
3. Clicking a historical version shows read-only view of that configuration (APIs, prompt, model, section order)
4. Diff view compares any two versions (highlighting added/removed/changed elements)
5. "Rollback to This Version" button allows restoring a previous configuration as current active version
6. Rollback creates new version (not true revert) and logs as audit event
7. Confirmation modal before rollback warns that current production config will be replaced
8. Version history infinite retention as per data retention policy (NFR15)
9. Meets requirement for configuration versioning and history maintenance
10. Version metadata includes: which model was used for testing, cost of test generations, number of test iterations

### Story 5.5: Production Integration and Active Configuration API

**As a** backend developer (of existing news generation system),
**I want** a stable API to fetch active configurations for triggers,
**so that** automated news generation can use CMS-published configurations.

**Acceptance Criteria**:
1. Backend endpoint `GET /api/triggers/:id/active-config` returns currently active published configuration
2. Response includes all necessary data: APIs to call, parser settings, section order, prompt template, selected LLM model, model settings
3. API versioned (e.g., `/api/v1/`) to support future changes without breaking existing integrations
4. Authentication required using cookies (compatible with existing authentication system)
5. Response cached (short TTL, e.g., 5 minutes) to reduce database load from automated polling
6. 404 returned if no active configuration exists for trigger (with clear error message)
7. Documentation (OpenAPI/Swagger) auto-generated by FastAPI describes endpoint
8. Integration test validates that published configuration is immediately accessible via this endpoint
9. Backward compatibility maintained with existing news generation system expectations
10. Logging of all API calls for monitoring integration health

## Checklist Results Report

### Executive Summary

**Overall PRD Completeness**: 88% (120/137 checklist items passed)

**MVP Scope Appropriateness**: **Just Right** - The scope is well-balanced between delivering core value (configuration, testing, publishing workflow) and avoiding feature bloat. The 5-epic structure with 26 stories is appropriate for a 3-4 month MVP timeline.

**Readiness for Architecture Phase**: **Nearly Ready** - The PRD provides excellent technical guidance and clear requirements. A few areas need minor clarification before architecture work begins, but none are blockers.

**Most Critical Gaps**:
1. Missing stakeholder identification and approval process definition
2. No availability/SLA requirements for production system
3. Monitoring and alerting strategy needs detail
4. Data quality requirements not explicitly defined

### Category Analysis

| Category                         | Status  | Score | Critical Issues                                      |
| -------------------------------- | ------- | ----- | ---------------------------------------------------- |
| 1. Problem Definition & Context  | PARTIAL | 79%   | Missing user research details, competitive analysis  |
| 2. MVP Scope Definition          | PASS    | 100%  | None                                                 |
| 3. User Experience Requirements  | PASS    | 100%  | None                                                 |
| 4. Functional Requirements       | PASS    | 100%  | None                                                 |
| 5. Non-Functional Requirements   | PARTIAL | 76%   | Missing availability SLA, backup/recovery strategy   |
| 6. Epic & Story Structure        | PASS    | 100%  | None                                                 |
| 7. Technical Guidance            | PARTIAL | 82%   | Monitoring details, documentation requirements light |
| 8. Cross-Functional Requirements | PARTIAL | 81%   | Data quality, support requirements undefined         |
| 9. Clarity & Communication       | PARTIAL | 60%   | No diagrams, stakeholder mgmt plan missing           |

### Top Issues by Priority

#### BLOCKERS (Must Fix Before Architect Proceeds)
*None identified* - The PRD is sufficiently complete for architecture work to begin.

#### HIGH PRIORITY (Should Fix for Quality)

1. **Define System Availability Requirements (NFR)**
   - **Issue**: No SLA or uptime target specified for production system
   - **Impact**: Architect cannot design for appropriate reliability level
   - **Recommendation**: Add NFR: "System shall maintain 99% uptime during business hours (9am-6pm EST, Mon-Fri)" or similar based on business needs
   - **Owner**: PM to confirm with stakeholders

2. **Specify Backup and Disaster Recovery Strategy**
   - **Issue**: MongoDB backup, configuration versioning recovery not detailed
   - **Impact**: Risk of data loss, no recovery plan
   - **Recommendation**: Add requirement for daily MongoDB backups to S3, 30-day retention, 4-hour RPO
   - **Owner**: PM with Architect input

3. **Detail Monitoring and Alerting Requirements**
   - **Issue**: CloudWatch mentioned but no specifics on what to monitor or alert on
   - **Impact**: Production issues may go undetected
   - **Recommendation**: Add NFR: Alert on API errors >5%, generation failures >10%, response time >3s, AWS resource utilization >80%
   - **Owner**: PM with DevOps input

#### MEDIUM PRIORITY (Would Improve Clarity)

4. **Add Data Quality Requirements**
   - **Issue**: No validation rules for configuration data, stock IDs, prompts
   - **Impact**: Potential for invalid data in database
   - **Recommendation**: Define validation rules (e.g., stock ID format, prompt max length, required fields)
   - **Owner**: PM

5. **Define Support and Incident Response Process**
   - **Issue**: No plan for handling production issues, user support requests
   - **Impact**: Unclear responsibility when system fails or users need help
   - **Recommendation**: Document support model (e.g., Slack channel, email, on-call rotation)
   - **Owner**: PM with Operations

6. **Create User Flow Diagrams**
   - **Issue**: Complex workflows (trigger → data → prompt → generate → publish) described in text only
   - **Impact**: Harder for stakeholders to visualize, potential misalignment
   - **Recommendation**: Add flow diagram showing main configuration workflow
   - **Owner**: PM or UX (post-PRD, pre-architecture)

7. **Identify Stakeholders and Approval Process**
   - **Issue**: No list of who reviews/approves PRD, who signs off on MVP completion
   - **Impact**: Unclear decision-making authority
   - **Recommendation**: Add stakeholder section: content team lead, dev lead, product leadership
   - **Owner**: PM

#### LOW PRIORITY (Nice to Have)

8. **Document Actual User Research Findings**
   - **Issue**: PRD based on brief assumptions, not validated with real users
   - **Impact**: Risk of building wrong thing (mitigated by internal users who contributed to brief)
   - **Recommendation**: Conduct 3-5 user interviews with content managers to validate pain points and workflow
   - **Owner**: PM (can be done in parallel with development)

9. **Add Competitive Analysis Detail**
   - **Issue**: Brief mentions competitors fall short but doesn't name them or detail gaps
   - **Impact**: Missing context on market landscape
   - **Recommendation**: Research 2-3 comparable CMS tools, document why they don't fit
   - **Owner**: PM (optional)

10. **Define Documentation Requirements**
    - **Issue**: No explicit requirement for API docs, user guides, deployment runbooks
    - **Impact**: Documentation may be inconsistent or missing
    - **Recommendation**: Add story for API documentation (auto-generated by FastAPI), user guide (post-MVP), deployment runbook
    - **Owner**: PM to add to backlog

### MVP Scope Assessment

**Features That Could Be Cut for Leaner MVP**:
- **Version History & Rollback (Story 5.4)**: Could defer to Phase 2; publish-only for MVP, add rollback later
- **Audit Log UI (Story 5.3)**: Could keep backend logging but defer UI to Phase 2
- **Section Reordering (Story 3.1)**: Could default to parser-defined order for MVP, add reordering later
- **Prompt Version History (Story 3.5)**: Could simplify to single undo level, defer full history

**Recommendation**: Keep current scope. These features are valuable and stories are well-sized. Cutting them saves ~1-2 weeks but reduces confidence and usability significantly.

**Missing Features That Are Essential**:
*None identified* - The PRD comprehensively covers the end-to-end workflow from trigger selection to production publication.

**Complexity Concerns**:
1. **Parser Integration (Story 2.4)**: Assumes existing parsers can be easily integrated; may require more investigation
2. **Multi-Model Parallel Generation (Story 4.3)**: Async processing with SSE/polling adds complexity; consider synchronous sequential generation for MVP
3. **AWS Deployment (Story 1.6)**: No containerization may make deployment more brittle; consider Docker even if not using orchestration

**Timeline Realism**:
- **3-4 months for 26 stories = ~1.5-2 stories per week** - Reasonable for a small team (2-3 developers)
- **Epic 1 (6 stories) = 2-3 weeks** - Includes AWS setup which could take longer if infrastructure is greenfield
- **Risk**: Parser integration unknowns, LLM API reliability could cause delays
- **Mitigation**: Technical spikes in Epic 1 for parser integration, Epic 2 for LLM integration

**Overall Assessment**: Timeline is achievable but tight. Consider adding 10-20% buffer for unknowns.

### Technical Readiness

**Clarity of Technical Constraints**: **Excellent**
- Technology stack fully specified (Python/FastAPI, Next.js, MongoDB, AWS, Bootstrap)
- Architecture pattern clear (monolith, no containerization)
- Integration requirements detailed (data APIs, parsers, LLMs)

**Identified Technical Risks**:
1. **Parser Integration Complexity**: Existing parsers may have undocumented dependencies (flagged in brief)
2. **LLM Cost Overruns**: Heavy testing could exceed budget (cost tracking mitigates)
3. **Data API Reliability**: Real-time CMS use may expose issues not seen in batch processing (caching mitigates)
4. **No Containerization**: Deployment may be more fragile than Docker-based approach

**Areas Needing Architect Investigation**:
1. **Parser Integration Approach**: Determine if parsers are Python modules or standalone scripts; design adapter layer accordingly
2. **Async Job Processing**: Decide between synchronous (simpler) vs. async with SSE/polling (better UX) for news generation
3. **MongoDB Schema Design**: Design flexible schema for configurations, prompts (versioned), generation history
4. **LLM Provider Abstraction**: Design strategy pattern for multi-provider support with cost tracking
5. **Authentication Integration**: Confirm if SSO integration is available or if JWT-only for MVP
6. **Frontend Deployment**: Decide between static Next.js export (S3+CloudFront) vs. SSR (EC2 with Node.js)

### Recommendations

#### Immediate Actions (Before Architecture Phase)

1. **Add Availability & Backup NFRs**
   - Define uptime SLA (suggest 99% during business hours for internal tool)
   - Specify MongoDB backup strategy (daily to S3, 30-day retention)
   - **Effort**: 15 minutes

2. **Detail Monitoring Requirements**
   - List key metrics to monitor (API errors, generation failures, response times, costs)
   - Define alerting thresholds
   - **Effort**: 30 minutes

3. **Identify Stakeholders**
   - List who reviews/approves PRD (content team lead, dev lead, product leadership)
   - Define sign-off process for MVP completion
   - **Effort**: 15 minutes

#### Suggested Improvements (Optional, Before Development)

4. **Create User Flow Diagram**
   - Visual representation of trigger → data → prompt → generate → publish workflow
   - Helps UX designer and developer alignment
   - **Effort**: 1-2 hours

5. **Conduct User Validation Interviews**
   - 3-5 interviews with content managers to validate workflow and priorities
   - Can be done in parallel with Epic 1 development
   - **Effort**: 4-6 hours

6. **Technical Spike Stories**
   - Consider adding spike stories to Epic 1 for parser integration and LLM API testing
   - De-risks unknowns early
   - **Effort**: Already planned in architecture phase

#### Help with Refining MVP Scope

If timeline pressure increases, consider this phased approach:

**Phase 1 (Weeks 1-8): Core Workflow**
- Epics 1-4 (Foundation, Data, Prompts, Generation)
- Skip: Version history, audit UI, section reordering
- **Outcome**: Users can configure and test, but no production publishing

**Phase 2 (Weeks 9-12): Production Integration**
- Epic 5 + deferred features from Phase 1
- **Outcome**: Full MVP with publishing

### Final Decision

**NEARLY READY FOR ARCHITECT** ✅

The PRD is comprehensive, well-structured, and provides excellent guidance for architecture and development. The few identified gaps are minor and can be addressed quickly (estimated 1-2 hours total).

**Action Items Before Architect Handoff**:
1. Add availability SLA and backup strategy NFRs (15 min)
2. Detail monitoring and alerting requirements (30 min)
3. Identify stakeholders and approval process (15 min)

**Once these are addressed, the PRD will be READY FOR ARCHITECT.**

**Strengths of this PRD**:
- ✅ Exceptionally detailed user stories with comprehensive acceptance criteria
- ✅ Clear technical stack decisions with documented rationale
- ✅ Well-sequenced epics following agile best practices
- ✅ Appropriate MVP scope balancing value delivery and timeline
- ✅ Strong traceability from problem statement → goals → requirements → stories
- ✅ Thoughtful consideration of edge cases, error handling, and non-functional requirements throughout

**Congratulations - this is a high-quality PRD!** 🎉

## Next Steps

### UX Expert Prompt

Review the attached Product Requirements Document (PRD) for the AI-Powered News CMS. Your mission is to create a comprehensive UX/UI design specification that translates the product vision into detailed wireframes, user flows, and interaction patterns.

**Key Focus Areas**:
- Configuration Workspace (primary screen): Multi-panel layout with data preview, prompt editor (Monaco), and model selection
- Trigger-to-publish workflow: Ensure seamless progression through data → prompt → generate → publish stages
- Side-by-side model comparison interface for testing multiple LLM outputs
- Progressive disclosure pattern to manage complexity
- Bootstrap 5 component library (React-Bootstrap) adherence

**Deliverables**: Wireframes for core screens, detailed user flow diagrams, component specifications, and interaction patterns that align with the technical stack (Next.js, Bootstrap 5, Monaco Editor).

### Architect Prompt

Review the attached Product Requirements Document (PRD) for the AI-Powered News CMS. Your mission is to design the technical architecture that implements the requirements while adhering to the specified constraints.

**Technical Stack (Non-Negotiable)**:
- Backend: Python 3.11+ with FastAPI, Pydantic v2, Motor (async MongoDB driver)
- Frontend: Next.js with TypeScript, React-Bootstrap, Monaco Editor, React Context API
- Database: MongoDB Community Edition
- Infrastructure: AWS (EC2, S3, CloudWatch, Secrets Manager) - No containerization
- Architecture: Monolithic application

**Key Design Challenges**:
1. Parser integration layer (existing Python parsers - determine module vs. subprocess approach)
2. LLM provider abstraction with cost tracking (OpenAI, Anthropic, Google)
3. Async news generation with SSE or polling for real-time status updates
4. MongoDB schema design for versioned configurations and prompts
5. Data API adapter pattern for multiple financial data sources

**Investigation Required**:
- Parser script integration feasibility (Story 2.4 spike)
- Cookie-based authentication integration with existing system
- Frontend deployment approach (static export vs. SSR)

**Deliverables**: Architecture diagrams, API specifications, database schema design, deployment architecture, and technical risk mitigation strategies that enable the development team to begin implementation immediately.
