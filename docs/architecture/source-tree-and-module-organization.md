# Source Tree and Module Organization

## Planned Project Organization

### Backend Module Structure (Python/FastAPI)

**Story 1.1 - Initial Setup**:
```
backend/
├── app/
│   ├── main.py                 # FastAPI app initialization, CORS, middleware
│   ├── config.py               # Environment configuration, secrets loading
│   ├── database.py             # MongoDB connection setup (Motor)
│   ├── models/                 # Pydantic models for MongoDB documents
│   │   ├── trigger.py          # Trigger schema
│   │   ├── configuration.py    # Configuration schema (includes all 3 prompt types)
│   │   ├── user.py             # User schema
│   │   └── audit_log.py        # Audit log schema
│   ├── routers/                # API route handlers
│   │   ├── triggers.py         # Trigger management endpoints (Story 1.4)
│   │   ├── configuration.py    # Config CRUD endpoints (Epic 2-3)
│   │   ├── data.py             # Data fetch and parse endpoints (Epic 2)
│   │   ├── generation.py       # LLM generation endpoints (Epic 4)
│   │   └── health.py           # Health check endpoint (Story 1.2)
│   └── services/               # Business logic (to be created in later epics)
```

**Epic 2 - Data Pipeline**:
```
backend/app/
├── data_adapters/              # Financial data API integrations
│   ├── base.py                 # Abstract base adapter class
│   ├── earnings_api.py         # Earnings data adapter (Story 2.2)
│   ├── price_api.py            # Price data adapter (Story 2.2)
│   └── registry.py             # Adapter registry for dynamic lookup
├── parsers/                    # Parser script integration
│   ├── adapter.py              # Parser execution layer (Story 2.4)
│   └── (existing parsers TBD)  # Location of existing parser scripts unknown
```

**Epic 4 - LLM Integration**:
```
backend/app/
├── llm_providers/              # LLM abstraction layer
│   ├── base.py                 # Abstract LLMProvider class
│   ├── openai_provider.py      # OpenAI integration (Story 4.1)
│   ├── anthropic_provider.py   # Anthropic integration (Story 4.1)
│   ├── google_provider.py      # Google AI integration (Story 4.1)
│   └── registry.py             # Provider registry
```

### Frontend Module Structure (Next.js/React)

**Story 1.1, 1.3 - Initial Setup**:
```
frontend/src/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout with Bootstrap CSS
│   ├── page.tsx                # Dashboard (trigger selector)
│   ├── config/
│   │   └── [triggerId]/
│   │       └── page.tsx        # Configuration Workspace
│   └── globals.css             # Global styles
├── components/                 # React components
│   ├── layout/
│   │   ├── Navbar.tsx          # Top navigation (Story 1.3)
│   │   ├── Footer.tsx          # Footer
│   │   └── Breadcrumb.tsx      # Breadcrumb navigation
│   ├── dashboard/
│   │   ├── TriggerSelector.tsx # Dropdown trigger selector (Story 1.4)
│   │   ├── QuickStats.tsx      # Stats cards
│   │   └── RecentActivity.tsx  # Activity list
│   ├── config/                 # Configuration Workspace panels (Epic 2-4)
│   │   ├── TriggerContextBar.tsx  # Stock ID + prompt type selection
│   │   ├── DataConfiguration.tsx  # Section selection + fetch (Epic 2)
│   │   ├── SectionManagement.tsx  # Drag-drop reordering (Epic 3)
│   │   ├── PromptEditor.tsx       # Tabbed Monaco Editor (Epic 3)
│   │   ├── ModelSelection.tsx     # Model checkboxes (Epic 4)
│   │   └── ResultsDisplay.tsx     # Grouped results (Epic 4)
│   └── common/
│       ├── Button.tsx          # Custom button component
│       ├── Card.tsx            # Card component
│       ├── Modal.tsx           # Modal wrapper
│       └── Toast.tsx           # Toast notifications
├── contexts/                   # React Context providers
│   ├── UserContext.tsx         # User session state
│   ├── ConfigContext.tsx       # Configuration state (Epic 2-4)
│   └── GenerationContext.tsx   # Generation results state (Epic 4)
├── lib/                        # Utilities and API clients
│   ├── api.ts                  # Axios/Fetch API client setup
│   └── utils.ts                # Helper functions
└── types/                      # TypeScript type definitions
    ├── trigger.ts
    ├── configuration.ts
    └── generation.ts
```

## Key Modules and Their Purpose (Planned)

**Backend**:
- **main.py**: FastAPI app initialization, middleware, CORS (Story 1.1)
- **database.py**: MongoDB connection with Motor async driver (Story 1.2)
- **routers/triggers.py**: GET /api/triggers, GET /api/triggers/:id/config (Story 1.4)
- **data_adapters/**: Adapters for financial data APIs with retry and rate limiting (Epic 2)
- **parsers/adapter.py**: Execute existing parser scripts to transform data (Epic 2)
- **llm_providers/**: Unified LLM abstraction for OpenAI, Anthropic, Google (Epic 4)

**Frontend**:
- **app/page.tsx**: Dashboard with dropdown trigger selector (Story 1.4)
- **app/config/[triggerId]/page.tsx**: Configuration Workspace main page (Epic 2-4)
- **components/config/PromptEditor.tsx**: Tabbed Monaco Editor for multi-prompt types (Epic 3)
- **components/config/ResultsDisplay.tsx**: Grouped results by prompt type → model (Epic 4)
- **contexts/ConfigContext.tsx**: Manages configuration state across all panels (Epic 2-4)
