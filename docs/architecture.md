# AI-Powered News CMS - Project Architecture Document

## Introduction

This document captures the **CURRENT STATE** and **PLANNED ARCHITECTURE** of the AI-Powered News CMS project for equity market research. As this is a greenfield project (starting from scratch), this document serves as both a reference for the initial planning state and a blueprint for implementation.

### Document Scope

This architecture document is **focused on the planned News CMS implementation** as defined in the PRD (docs/prd.md). It provides:
- Current project state (planning phase, infrastructure setup)
- Planned technical architecture based on PRD requirements
- Implementation roadmap organized by Epic
- Integration points with existing equity market research platform
- Technical constraints and decisions already made in the PRD

### Document Status

**Project Phase**: Epic 1 - Foundation & Core Infrastructure (Story 1.5a in progress)

**Last Updated**: 2025-10-29

### Change Log

| Date       | Version | Description                    | Author  |
|------------|---------|--------------------------------|---------|
| 2025-10-29 | 1.0     | Initial architecture document  | Winston |

## Quick Reference - Key Files and Entry Points

### Current Project Structure

```
news/
├── .bmad-core/              # BMAD™ Core agent framework
├── .claude/                 # Claude Code slash commands
├── docs/                    # Project documentation
│   ├── prd.md               # **PRIMARY**: Product Requirements Document
│   ├── front-end-spec.md    # UI/UX Specification (v2.2)
│   ├── CHANGELOG-epic1-api-setup.md  # Epic 1 Story 1.5a addition
│   └── figma-ai-complete-prompts-v2.md  # Design prompts
├── scripts/                 # Utility scripts
│   └── test-api-keys.py     # API key validation script (Story 1.5a)
└── README.md                # (To be created)
```

### Critical Files for Understanding the System

- **Requirements**: [docs/prd.md](docs/prd.md) - Complete product requirements and epic breakdown
- **UI/UX Specification**: [docs/front-end-spec.md](docs/front-end-spec.md) - Detailed user interface design
- **API Key Setup**: [scripts/test-api-keys.py](scripts/test-api-keys.py) - Third-party API validation
- **Epic 1 Changes**: [docs/CHANGELOG-epic1-api-setup.md](docs/CHANGELOG-epic1-api-setup.md) - Story 1.5a details

### What Does NOT Exist Yet

**Backend**: No Python/FastAPI backend code exists. Backend will be created in Epic 1 (Stories 1.1-1.6).

**Frontend**: No Next.js/React frontend code exists. Frontend will be created in Epic 1 (Stories 1.1, 1.3, 1.4).

**Database**: MongoDB is not yet set up. Database setup is Story 1.2 of Epic 1.

**Infrastructure**: AWS deployment infrastructure does not exist. Infrastructure setup is Story 1.6 of Epic 1.

**Parsers**: Existing parser scripts are assumed to exist in the main equity research platform but are NOT yet integrated or documented.

**Data APIs**: External financial data API integrations do not exist yet. These will be built in Epic 2.

## High Level Architecture

### Project Type: Greenfield (New Development)

This is a **NEW internal tool** being built from scratch for the equity market research platform. While it will integrate with existing systems (parser scripts, authentication, production news generation pipeline), the CMS itself has no legacy code.

### Technical Summary

**Architecture Pattern**: Monolithic Application (No Microservices, No Containerization)

**Deployment Model**: Direct deployment to AWS EC2 with Nginx reverse proxy

**Development Status**: Planning phase → Epic 1 implementation beginning

### Planned Tech Stack

| Category            | Technology           | Version  | Status              | Notes                                        |
|---------------------|----------------------|----------|---------------------|----------------------------------------------|
| **Backend Runtime** | Python               | 3.11+    | ❌ Not setup        | To be installed in Story 1.1                 |
| **Backend Framework** | FastAPI            | Latest   | ❌ Not setup        | Story 1.1 - REST API with auto OpenAPI docs  |
| **Validation**      | Pydantic             | v2       | ❌ Not setup        | Story 1.1 - Runtime validation + type hints  |
| **Database Driver** | Motor (PyMongo async) | Latest | ❌ Not setup        | Story 1.2 - Async MongoDB driver             |
| **Frontend Runtime** | Node.js             | 18.x LTS | ❌ Not setup        | Story 1.1                                    |
| **Frontend Framework** | Next.js           | 14+      | ❌ Not setup        | Story 1.1 - App Router with TypeScript       |
| **UI Library**      | React-Bootstrap      | Latest   | ❌ Not setup        | Story 1.3 - Bootstrap 5 components           |
| **Code Editor**     | Monaco Editor        | Latest   | ❌ Not setup        | Story 3.2 - Prompt editing with syntax highlighting |
| **State Management** | React Context API   | Built-in | ❌ Not setup        | Story 1.3 - Separate contexts per concern    |
| **Database**        | MongoDB Community    | 5.0+     | ❌ Not setup        | Story 1.2 - NoSQL for flexible schemas       |
| **Deployment**      | AWS EC2              | t3.medium | ❌ Not setup       | Story 1.6 - No containerization              |
| **Web Server**      | Nginx                | Latest   | ❌ Not setup        | Story 1.6 - Reverse proxy + SSL termination  |
| **Secrets**         | AWS Secrets Manager  | N/A      | ⚠️ Partial (Story 1.5a) | LLM API keys being configured          |
| **LLM Providers**   | OpenAI               | GPT-4, GPT-3.5 | ⚠️ Story 1.5a in progress | Epic 4 integration |
|                     | Anthropic            | Claude 3 | ⚠️ Story 1.5a in progress | Epic 4 integration                           |
|                     | Google AI            | Gemini Pro | ⚠️ Story 1.5a in progress | Epic 4 integration                         |

**Legend**:
- ✅ Implemented and working
- ⚠️ Partial implementation or in progress
- ❌ Not yet implemented
- 🔄 Planned/documented but not started

### Repository Structure Reality Check

**Current State**: Single project directory with documentation and planning artifacts only.

**Planned Structure** (from PRD):
```
news-cms/
├── frontend/              # Next.js/React application (Epic 1, Story 1.1)
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # React components (Bootstrap)
│   │   ├── contexts/      # React Context providers
│   │   ├── lib/           # Utility functions, API clients
│   │   └── types/         # TypeScript type definitions
│   ├── public/            # Static assets
│   ├── package.json
│   └── tsconfig.json
├── backend/               # Python/FastAPI application (Epic 1, Story 1.1)
│   ├── app/
│   │   ├── main.py        # FastAPI application entry point
│   │   ├── routers/       # API route handlers
│   │   ├── models/        # Pydantic models (data schemas)
│   │   ├── services/      # Business logic layer
│   │   ├── data_adapters/ # Financial data API integrations (Epic 2)
│   │   ├── parsers/       # Parser script integration (Epic 2)
│   │   ├── llm_providers/ # LLM abstraction layer (Epic 4)
│   │   └── utils/         # Helper functions
│   ├── tests/             # pytest test suite
│   ├── requirements.txt   # Python dependencies
│   └── pyproject.toml     # Python project config
├── shared/                # Shared schemas (optional for MVP)
├── scripts/               # ✅ Deployment and utility scripts
│   └── test-api-keys.py   # ✅ API key validation (Story 1.5a)
├── docs/                  # ✅ Project documentation
│   ├── prd.md             # ✅ Product Requirements
│   ├── front-end-spec.md  # ✅ UI/UX Specification
│   ├── architecture.md    # ✅ This document
│   └── api/               # (Future) OpenAPI specs, Postman collections
├── .env.example           # Environment variable template (Story 1.2)
├── .gitignore             # (To be created in Story 1.1)
└── README.md              # (To be created in Story 1.1)
```

**Type**: Monorepo (single repository with frontend/, backend/ directories)

**Package Manager** (Planned):
- Backend: pip with virtual environment (venv)
- Frontend: npm or pnpm (to be decided in Story 1.1)

## Source Tree and Module Organization

### Planned Project Organization

#### Backend Module Structure (Python/FastAPI)

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

#### Frontend Module Structure (Next.js/React)

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

### Key Modules and Their Purpose (Planned)

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

## Data Models and APIs

### Planned Data Models

**Note**: These models do not exist yet. They will be created as Pydantic models in backend/app/models/ during Epic 1, Story 1.2.

#### Trigger Model
```python
# backend/app/models/trigger.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Trigger(BaseModel):
    id: str = Field(alias="_id")
    name: str                           # e.g., "Earnings Alert"
    description: str
    trigger_type: str                   # e.g., "earnings", "price_movement"
    status: str                         # "configured" | "unconfigured" | "in_progress"
    last_updated: datetime
    created_at: datetime
    created_by: str                     # User ID
```

#### Configuration Model (Multi-Prompt Type Support)
```python
# backend/app/models/configuration.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional

class PromptConfig(BaseModel):
    template: str
    version_history: List[Dict]         # List of {template, timestamp, user_id}
    last_test_generation: Optional[Dict]  # {timestamp, stock_id, results}

class Configuration(BaseModel):
    id: str = Field(alias="_id")
    trigger_id: str
    version: int

    # SHARED across all prompt types (configured once, applies to all)
    data_sections: List[str]            # Selected section IDs (e.g., ["1", "2", "3", "5", "7"])
    section_order: List[str]            # Order of sections
    model_config: Dict                  # {selected_models, temperature, max_tokens}

    # SEPARATE per prompt type (independent templates)
    prompts: Dict[str, PromptConfig]    # {"paid": PromptConfig, "unpaid": PromptConfig, "crawler": PromptConfig}

    # Metadata
    created_by: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    is_active: bool                     # True if production version
```

#### User Model
```python
# backend/app/models/user.py
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str = Field(alias="_id")
    username: str
    email: str
    role: str                           # "content_manager" | "analyst" | "team_lead"
    created_at: datetime
```

#### Audit Log Model
```python
# backend/app/models/audit_log.py
from pydantic import BaseModel
from datetime import datetime
from typing import Dict

class AuditLog(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    action: str                         # "created", "updated", "published", "api_added", "prompt_edited"
    trigger_id: str
    timestamp: datetime
    details: Dict                       # JSON diff or action details
```

#### Frontend Section Interface (TypeScript)
```typescript
// frontend/src/components/SectionManagementPanel.tsx
export interface Section {
  id: string;                           // OLD data: 'old' | NEW data: '1'-'14'
  name: string;                         // OLD: 'Old Data' | NEW: section names
  source?: 'old' | 'new';               // Track data source for visual badges
}
```

**OLD Data Handling**:
- OLD data from `news_triggers.data` is **treated as a single section**
- NOT split into 14 sections like NEW data
- Section object: `{id: 'old', name: 'Old Data', source: 'old'}`
- Blue badge (info variant) for visual distinction

**NEW Data Handling**:
- NEW data from `generate_full_report.py` contains 14 sections (1-14)
- Each section: `{id: '1'-'14', name: 'Section Name', source: 'new'}`
- Green badge (success variant) for visual distinction

**Data Persistence (localStorage)**:
- Keys: `fetchedOldData_{triggerId}`, `fetchedNewData_{triggerId}`, `selectedSections_{triggerId}`
- Prevents re-fetching when switching between OLD/NEW/OLD_NEW modes
- Cleared only on explicit user action or new trigger selection

**Section Management Panel**:
- Displays ONLY selected/visible sections (no visibility toggles)
- Source badges: OLD (blue/#0dcaf0) | NEW (green/#198754)
- Drag-and-drop reordering using React DnD
- Preview mode shows final output order

### Planned API Specifications

**Status**: APIs do not exist yet. Will be implemented throughout Epic 1-5.

**API Documentation**: FastAPI will auto-generate OpenAPI documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

#### Epic 1 - Foundation APIs

**Health Check** (Story 1.2):
```
GET /api/health
Response: { "status": "ok", "database": "connected", "timestamp": "..." }
```

**Trigger Management** (Story 1.4):
```
GET /api/triggers
Response: [{ "id": "...", "name": "...", "status": "...", "last_updated": "..." }, ...]

GET /api/triggers/:id/config
Response: { "trigger_id": "...", "data_sections": [...], "prompts": {...}, ... }
```

#### Epic 2 - Data Pipeline APIs

**API Configuration** (Story 2.1):
```
POST /api/triggers/:id/config/apis
Body: { "api_id": "earnings_api" }
Response: { "success": true, "configured_apis": [...] }

DELETE /api/triggers/:id/config/apis/:apiId
Response: { "success": true, "configured_apis": [...] }
```

**Data Retrieval** (Story 2.3):
```
POST /api/triggers/:id/data/fetch
Body: { "stock_id": "AAPL", "section_ids": ["1", "2", "3"] }
Response: { "raw_data": { "section_1": {...}, "section_2": {...} }, "status": {...} }
```

**Data Parsing** (Story 2.4):
```
POST /api/triggers/:id/data/parse
Body: { "raw_data": {...} }
Response: { "structured_data": { "sections": [...] }, "errors": [] }
```

#### Epic 4 - LLM Generation APIs

**Multi-Model Generation** (Story 4.3):
```
POST /api/triggers/:id/generate
Body: {
  "stock_id": "AAPL",
  "selected_models": ["gpt-4", "claude-3-sonnet"],
  "prompt_types": ["paid", "unpaid"],        # Only checked types
  "prompts": {
    "paid": "...",
    "unpaid": "..."
  },
  "structured_data": {...},
  "model_settings": {...}
}
Response (SSE stream or polling):
{
  "generation_id": "...",
  "status": {
    "paid": {
      "gpt-4": "generating",
      "claude-3-sonnet": "complete"
    },
    "unpaid": {
      "gpt-4": "pending",
      "claude-3-sonnet": "generating"
    }
  },
  "results": {
    "paid": {
      "gpt-4": null,
      "claude-3-sonnet": {
        "text": "...",
        "tokens": 456,
        "cost": 0.08,
        "latency": 8.3
      }
    },
    "unpaid": {...}
  }
}
```

#### Epic 5 - Publishing APIs

**Publish Configuration** (Story 5.2):
```
POST /api/triggers/:id/publish
Body: { "configuration": {...} }  # Includes all 3 prompt types
Response: { "success": true, "version": 2, "timestamp": "..." }
```

**Active Configuration** (Story 5.5):
```
GET /api/triggers/:id/active-config
Response: {
  "trigger_id": "...",
  "data_sections": [...],
  "prompts": {
    "paid": {...},
    "unpaid": {...},
    "crawler": {...}
  },
  "model_config": {...}
}
```

### MongoDB Collections Schema Design

**Collections** (to be created in Story 1.2):
- `triggers`: Trigger definitions
- `configurations`: Configuration versions (includes all 3 prompt types in single document)
- `users`: User accounts (may integrate with existing auth system)
- `audit_log`: Change tracking
- `generation_history`: Test generation results (session-level, 30-day retention)

**Indexes** (to be created):
- `triggers`: `{ trigger_id: 1 }`
- `configurations`: `{ trigger_id: 1, is_active: 1 }`, `{ version: -1 }`
- `audit_log`: `{ trigger_id: 1, timestamp: -1 }`, `{ user_id: 1 }`

## Integration Points and External Dependencies

### External Services (Planned)

| Service          | Purpose              | Integration Type | Status              | Key Files (Future)                          |
|------------------|----------------------|------------------|---------------------|---------------------------------------------|
| OpenAI           | LLM (GPT-4, GPT-3.5) | REST API         | ⚠️ API key setup (1.5a) | backend/app/llm_providers/openai_provider.py |
| Anthropic        | LLM (Claude 3)       | REST API         | ⚠️ API key setup (1.5a) | backend/app/llm_providers/anthropic_provider.py |
| Google AI        | LLM (Gemini Pro)     | REST API         | ⚠️ API key setup (1.5a) | backend/app/llm_providers/google_provider.py |
| AWS Secrets Manager | Secure key storage | AWS SDK (boto3) | ⚠️ Story 1.5a in progress | backend/app/config.py |
| MongoDB Atlas (or EC2) | Database         | MongoDB driver  | ❌ Not setup (Story 1.2) | backend/app/database.py |
| Financial Data APIs | Market data       | REST API (TBD)  | ❌ Not identified yet | backend/app/data_adapters/ |

**Note**: Specific financial data API providers not yet identified. This is flagged in CHANGELOG-epic1-api-setup.md as requiring product team input.

### Internal Integration Points (Existing Systems)

**Authentication System**:
- **Integration Type**: Cookie-based authentication
- **Status**: ❌ Not yet designed
- **Epic**: Epic 1 (Story 1.1 - to be determined)
- **Assumption**: Existing equity research platform has authentication system that can issue cookies
- **Risk**: Integration details unknown; may require investigation spike

**Parser Scripts**:
- **Location**: Unknown (assumed to exist in main platform codebase)
- **Integration Approach**: Direct Python module import OR subprocess calls
- **Status**: ❌ Not investigated yet
- **Epic**: Epic 2 (Story 2.4)
- **Risk**: HIGH - Parser integration feasibility unknown (flagged in PRD as technical risk)
- **Next Step**: Identify parser locations and interfaces before Epic 2

**Production News Generation Pipeline**:
- **Integration Type**: Shared MongoDB database OR REST API
- **Status**: ❌ Not designed yet
- **Epic**: Epic 5 (Story 5.5)
- **Approach**: CMS publishes configurations to MongoDB; existing system reads active configurations
- **Alternative**: Expose GET /api/triggers/:id/active-config for existing system to poll

### Data Flow Between Systems

**Planned Integration Flow** (Epic 5):
```
[News CMS - Configuration Published]
         ↓
[MongoDB - configurations collection, is_active = true]
         ↓
[Existing Production News System - Reads Active Config]
         ↓
[Calls Data APIs + Parsers + LLM based on CMS config]
         ↓
[Publishes News to End Users]
```

**Key Integration Questions** (Require Investigation):
1. **Parser Integration**: Where are parser scripts located? Python modules or standalone scripts?
2. **Authentication**: Cookie format? Session validation endpoint? JWT tokens?
3. **Financial Data APIs**: Which providers? API keys already exist or need procurement?
4. **Production Pipeline**: MongoDB read pattern or REST API polling?

## Development and Deployment

### Local Development Setup (Planned)

**Status**: ❌ Not yet documented. Will be created in Story 1.1 README.md.

**Planned Setup Steps**:
1. Install Python 3.11+ and Node.js 18.x
2. Clone repository
3. Backend setup:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp ../.env.example .env   # Configure local MongoDB, API keys
   uvicorn app.main:app --reload  # Runs on http://localhost:8000
   ```
4. Frontend setup:
   ```bash
   cd frontend
   npm install
   npm run dev  # Runs on http://localhost:3000
   ```
5. MongoDB setup:
   - Option 1: Install MongoDB Community Edition locally
   - Option 2: Use MongoDB Atlas free tier for development
   - Run seed script: `python scripts/seed_data.py`

**Environment Variables** (from .env.example, to be created):
```
# Backend (.env)
MONGODB_URI=mongodb://localhost:27017/news_cms_dev
AWS_REGION=us-east-1
AWS_SECRETS_MANAGER_PREFIX=news-cms/
OPENAI_API_KEY=<from Secrets Manager or local for dev>
ANTHROPIC_API_KEY=<from Secrets Manager or local for dev>
GOOGLE_API_KEY=<from Secrets Manager or local for dev>
USE_MOCK_DATA=false  # Set to true to bypass real API calls
```

### Build and Deployment Process (Planned - Story 1.6)

**Status**: ❌ Not implemented yet. Epic 1, Story 1.6.

**Deployment Architecture** (AWS EC2, No Containerization):
```
[User Browser]
     ↓ HTTPS (443)
[CloudFront or ALB - SSL Termination]
     ↓
[EC2 Instance - t3.medium]
  ├── Nginx (Reverse Proxy)
  │    ├── /api → localhost:8000 (FastAPI backend)
  │    └── /    → localhost:3000 (Next.js frontend OR static files)
  ├── FastAPI (uvicorn) - systemd service
  └── Next.js (if SSR) OR S3+CloudFront (if static export)
     ↓
[MongoDB - Dedicated EC2 OR MongoDB Atlas]
```

**Deployment Options** (Decision needed in Story 1.6):
1. **Option A**: Next.js SSR on same EC2, Nginx proxies to Node.js
2. **Option B**: Next.js static export → S3 + CloudFront, API on EC2

**CI/CD Pipeline** (Planned - GitHub Actions):
```
[Push to develop branch]
     ↓
[GitHub Actions Workflow]
  ├── Lint (flake8, eslint)
  ├── Test (pytest, jest)
  ├── Build (pip install, npm build)
  └── Deploy to Staging EC2
     ↓
[Manual Approval]
     ↓
[Deploy to Production EC2]
```

**Environments**:
- **Development**: Local (developer machines)
- **Staging**: AWS EC2 (staging environment for QA)
- **Production**: AWS EC2 (production environment)

### AWS Infrastructure Requirements (Story 1.6)

**Resources to Provision**:
- EC2 instance (t3.medium) for staging
- EC2 instance (t3.medium) for production
- MongoDB EC2 instance OR MongoDB Atlas cluster
- S3 bucket for logs, backups, static assets (if using static export)
- CloudWatch Logs for application logs
- AWS Secrets Manager secrets:
  - `news-cms/llm/openai/api-key`
  - `news-cms/llm/anthropic/api-key`
  - `news-cms/llm/google/api-key`
  - `news-cms/db/mongodb-uri`
  - `news-cms/auth/jwt-secret` (if applicable)
- IAM role for EC2 instance with Secrets Manager read access
- SSL certificate via AWS Certificate Manager
- Security groups: Allow 80, 443 inbound; 8000, 3000 internal only

## Current Implementation Status

### Completed Work

✅ **Documentation Phase** (Epic 0 - Pre-development):
- PRD created and reviewed (88% completeness, nearly ready for architect)
- UI/UX Specification v2.2 completed (multi-prompt type support)
- Epic 1 Story 1.5a added (Third-Party API Setup)

⚠️ **Story 1.5a - Third-Party API Setup** (IN PROGRESS):
- API key acquisition process documented
- test-api-keys.py script created for validation
- OpenAI, Anthropic, Google AI account creation in progress
- AWS Secrets Manager configuration pending
- Billing alerts and cost monitoring setup pending

### Not Yet Started

❌ **Epic 1 - Foundation & Core Infrastructure**:
- Story 1.1: Project Setup and Monorepo Structure
- Story 1.2: MongoDB Database Setup and Connection
- Story 1.3: Basic UI Shell and Navigation
- Story 1.4: Trigger Management Dashboard
- Story 1.6: AWS Deployment Setup for Staging Environment

❌ **Epic 2-5**: All stories not started (Epic 1 prerequisite)

### Known Gaps and Technical Debt (Before Any Code Written)

**High Priority Investigations Needed**:
1. **Parser Integration** (Epic 2 Blocker):
   - Location of existing parser scripts unknown
   - Parser input/output format undocumented
   - Integration approach (module import vs. subprocess) undecided
   - **Action**: Technical spike in Epic 1 or early Epic 2

2. **Financial Data API Providers** (Epic 2 Blocker):
   - Specific providers not identified
   - API contracts unknown
   - API keys not yet procured
   - **Action**: Product team decision needed (flagged in CHANGELOG)

3. **Authentication Integration** (Epic 1 Risk):
   - Existing authentication system interface unknown
   - Cookie format, session validation endpoint undocumented
   - **Action**: Investigation before Story 1.1 completion

4. **Production Integration** (Epic 5 Risk):
   - Existing news generation pipeline architecture unknown
   - Configuration consumption pattern undecided (MongoDB vs. REST API)
   - **Action**: Design decision before Epic 5

### Technical Risks and Mitigation

| Risk                          | Likelihood | Impact | Mitigation Strategy                                      | Epic  |
|-------------------------------|------------|--------|----------------------------------------------------------|-------|
| Parser integration complexity | High       | High   | Technical spike in Epic 1; mock parsers for development  | 2     |
| LLM cost overruns             | Medium     | Medium | Cost tracking, spending limits, mock mode for dev        | 4     |
| Data API reliability          | Medium     | Medium | Retry logic, circuit breakers, caching                   | 2     |
| Authentication integration    | Medium     | High   | Early investigation spike; fallback to simple JWT        | 1     |
| MongoDB schema flexibility    | Low        | Medium | Pydantic validation at app layer; versioned migrations   | 1-5   |
| AWS deployment complexity     | Medium     | Medium | Thorough Story 1.6 planning; staging environment testing | 1     |
| No containerization fragility | Medium     | Low    | Ansible/systemd for deployment automation                | 1     |

## Epic-by-Epic Implementation Roadmap

### Epic 1: Foundation & Core Infrastructure (Weeks 1-3)

**Goal**: Establish deployable "walking skeleton" with trigger management.

**Stories**:
1. ⚠️ **Story 1.5a** (IN PROGRESS): Third-Party API Setup
   - Complete API key acquisition (OpenAI, Anthropic, Google)
   - Store all keys in AWS Secrets Manager
   - Configure billing alerts
   - Run test-api-keys.py successfully
   - **Blockers**: Anthropic API approval (1-2 days), financial data API provider selection

2. ❌ **Story 1.1**: Project Setup and Monorepo Structure
   - Create frontend/ and backend/ directories
   - Initialize package.json (frontend) and requirements.txt (backend)
   - Configure TypeScript, ESLint, pytest
   - Create .gitignore, README.md
   - Both apps run locally (uvicorn, npm run dev)

3. ❌ **Story 1.2**: MongoDB Database Setup and Connection
   - Install MongoDB or configure Atlas
   - Create Pydantic models (Trigger, Configuration, User, AuditLog)
   - Establish Motor async connection in FastAPI
   - Health check endpoint: GET /api/health
   - Seed script populates sample triggers

4. ❌ **Story 1.3**: Basic UI Shell and Navigation
   - Next.js layout with Bootstrap 5 CSS
   - Navbar with logo, Dashboard link, user info
   - Footer
   - Responsive grid system tested at 1200px, 768px
   - Loading spinner component

5. ❌ **Story 1.4**: Trigger Management Dashboard
   - GET /api/triggers endpoint
   - Dashboard page with dropdown trigger selector
   - Quick stats cards (Total Triggers, Configured, Last Updated)
   - Recent Activity list
   - Navigate to /config/:triggerId on selection
   - Loads in <2 seconds (NFR1)

6. ❌ **Story 1.6**: AWS Deployment Setup for Staging Environment
   - Provision EC2 t3.medium for staging
   - Install MongoDB on dedicated EC2 or configure Atlas
   - Deploy FastAPI as systemd service (uvicorn)
   - Deploy Next.js (decision: SSR on EC2 OR static to S3+CloudFront)
   - Nginx reverse proxy with SSL (AWS Certificate Manager)
   - GitHub Actions CI/CD to staging
   - Health check accessible via HTTPS
   - **Dependencies**: Story 1.5a complete (secrets available)

**Epic 1 Exit Criteria**:
- All APIs secured in Secrets Manager
- Monorepo structure established
- MongoDB connected and seeded
- Trigger dashboard displays triggers
- Staging environment deployed and accessible
- CI/CD pipeline deploys on push to develop

### Epic 2: Data Pipeline & Integration (Weeks 4-6)

**Goal**: Build data retrieval and transformation pipeline.

**Stories**:
1. ❌ **Story 2.1**: API Configuration Interface
   - Configuration Workspace page (frontend)
   - Trigger Context Bar with Stock ID input + prompt type checkboxes
   - Section Selection Dropdown (14 hardcoded sections, 5 pre-selected by backend)
   - "Use This Data" button (enabled by default)
   - POST /api/triggers/:id/config/sections, DELETE endpoints

2. ❌ **Story 2.2**: Data API Integration Layer
   - Create data_adapters/ module
   - Base DataAPIAdapter abstract class
   - 2+ concrete adapters (depends on financial API provider selection - BLOCKER)
   - Retry logic, rate limiting, request logging
   - Unit tests with mocked HTTP responses

3. ❌ **Story 2.3**: Data Retrieval and Raw JSON Display
   - POST /api/triggers/:id/data/fetch endpoint
   - Fetch data from configured APIs in parallel
   - Return raw JSON per section
   - Frontend displays collapsible JSON panels with syntax highlighting
   - Status indicators (success/failure, latency)
   - Completes within 5 seconds per API (NFR2)

4. ❌ **Story 2.4**: Parser Integration and Execution
   - Create parsers/adapter.py
   - Support module import OR subprocess execution (depends on parser investigation - BLOCKER)
   - POST /api/triggers/:id/data/parse endpoint
   - Parser timeout mechanism (10 seconds default)
   - Graceful error handling with actionable messages
   - Unit tests with sample JSON inputs

5. ❌ **Story 2.5**: Structured Data Display and Section Preview
   - Frontend displays parsed sections in Bootstrap Cards
   - Collapsible sections
   - Visual mapping (which API → which section)
   - "Preview Final Data Structure" button → JSON modal
   - Data persists in React Context for use in prompts

**Epic 2 Exit Criteria**:
- Section selection dropdown works with default selections
- Data fetched from APIs and displayed as raw JSON
- Parser executes and transforms data to structured sections
- Structured data displayed with clear labels
- Data available for prompt substitution

**Epic 2 Blockers**:
- Financial data API providers must be identified (product team decision)
- Parser script locations and interfaces must be documented

### Epic 3: Prompt Engineering Workspace (Weeks 7-9)

**Goal**: Create prompt editing environment with multi-prompt type support.

**Stories**:
1. ❌ **Story 3.1**: Section Reordering Interface (Shared Across All Prompt Types)
   - "Section Management" panel
   - Displays only selected sections from Data Configuration
   - Drag-and-drop sortable list (React DnD)
   - Number input alternative for accessibility
   - "Preview Data Structure" button
   - Section order saved to MongoDB

2. ❌ **Story 3.2**: Tabbed Prompt Editor with Syntax Highlighting
   - Monaco Editor component integrated
   - Tabbed interface: [💰 Paid] [🆓 Unpaid] [🕷️ Crawler]
   - Tab visibility controlled by Trigger Context Bar checkboxes
   - Paid tab always visible and active by default
   - Each tab maintains independent template and undo/redo stack
   - Syntax highlighting for placeholders ({{variable}})
   - Word/character count per tab
   - Auto-save every 5 seconds (debounced) per prompt type

3. ❌ **Story 3.3**: Data Placeholder Validation (Per Prompt Type)
   - Real-time parsing of placeholders for active tab only
   - Invalid placeholders underlined in red with tooltips
   - Valid placeholders show green checkmark
   - Autocomplete suggestions when typing {{
   - Validation error summary panel with line numbers
   - Tab indicator shows warning icon if errors in that tab's prompt

4. ❌ **Story 3.4**: Prompt Preview with Data Substitution (Per Prompt Type)
   - "Preview Final Prompt" button for active tab
   - Modal displays final prompt with actual data substituted
   - Missing data shown with red placeholder warning
   - Preview updates automatically when data/section order/tab changes
   - Estimated token count displayed
   - "Copy to Clipboard" button
   - Modal can show tabs to preview all checked prompt types

5. ❌ **Story 3.5**: Prompt Version History and Undo (Per Prompt Type)
   - Prompt changes tracked in local history per tab
   - Undo/Redo buttons (Ctrl+Z, Ctrl+Y) per tab
   - Version history panel shows last 10 versions per prompt type
   - Clicking version loads that prompt into editor for corresponding type
   - History persisted in sessionStorage (separate per type)
   - "Save as New Version" button for checkpointing per type

**Epic 3 Exit Criteria**:
- Sections can be reordered (only selected sections shown)
- Tabbed prompt editor works with 3 independent prompt types
- Placeholder validation catches errors per tab
- Prompt preview shows final prompt with data substituted per type
- Version history tracks changes per prompt type

### Epic 4: Multi-Model Generation & Testing (Weeks 10-12)

**Goal**: Implement LLM integration and multi-model testing workflow.

**Stories**:
1. ❌ **Story 4.1**: LLM Abstraction Layer and Provider Integration
   - Create llm_providers/ module
   - Base LLMProvider abstract class
   - OpenAI, Anthropic, Google AI concrete implementations
   - API authentication from AWS Secrets Manager
   - Cost calculation logic per provider
   - Rate limiting, retry logic
   - Provider registry for dynamic lookup
   - Unit tests with mocked API responses
   - Integration tests against real APIs (low-cost models)

2. ❌ **Story 4.2**: Model Selection Interface (Shared Across All Prompt Types)
   - "Model Selection" panel with header "(Used for All Types)"
   - Model cards grouped by provider (OpenAI, Anthropic, Google)
   - Checkboxes for model selection
   - Settings: temperature slider, max tokens input
   - **Cost estimate**: (selected models × checked prompt types)
   - Example: "2 models × 3 prompt types = 6 generations total"
   - Visual indicator: "Will generate for: Paid, Unpaid, Crawler"
   - Model selection saved to Configuration

3. ❌ **Story 4.3**: Parallel News Generation (For Checked Prompt Types)
   - POST /api/triggers/:id/generate endpoint
   - Backend initiates parallel LLM API calls using asyncio
   - Calculation: models × checked prompt types = total API calls
   - Frontend displays real-time status indicators (SSE or polling)
   - Status grouped by prompt type → model (Pending, Generating, Complete, Failed)
   - Progress: "Generating 4 of 6 complete"
   - Completes within 30 seconds timeout per model (NFR3)
   - Failed generations show error without blocking others
   - Results stored in generation_history collection

4. ❌ **Story 4.4**: Grouped Result Comparison (By Prompt Type → Model)
   - "Results & Comparison" panel
   - **Hierarchical Display**: Prompt Type Groups (collapsible) → Model Columns (side-by-side)
   - **Group 1**: 💰 Paid Prompt Results (blue header #0d6efd)
     - Side-by-side model columns (2-3 models)
     - Each result: model name, generated text, metadata
   - **Group 2**: 🆓 Unpaid Prompt Results (green header #198754)
     - Same layout as Group 1
   - **Group 3**: 🕷️ Crawler Prompt Results (orange header #fd7e14)
     - Same layout as Group 1
   - Metadata per result: 🎯 Tokens: 456 | ⏱️ Time: 8.3s | 💰 Cost: $0.08 (actual values)
   - Responsive: 2-3 columns on desktop, stacked on tablet
   - Visual outlier indicators within each group
   - "Copy" button per result

5. ❌ **Story 4.5**: Iterative Refinement Workflow
   - "Regenerate" button (regenerates for checked types and selected models)
   - Inline prompt editing available after results
   - "What Changed" tooltip shows diff between iterations
   - Iteration history timeline (collapsible, below results)
   - Timeline shows: iteration number, timestamp, which prompt types tested, changes made
   - Clicking historical generation loads that config and results
   - Debounced auto-save prevents losing changes
   - Quick cycle: edit → regenerate → compare in <60 seconds

6. ❌ **Story 4.6**: Post-Generation Metadata Display
   - Metadata container below each result card
   - Label: "⚡ ACTUAL METRICS" (subtle background #f8f9fa)
   - 🎯 Tokens Used: actual token count from LLM API
   - ⏱️ Time Taken: generation time in seconds (8.3s)
   - 💰 Actual Cost: calculated from actual tokens ($0.08)
   - Visual comparison: estimated vs. actual cost (diff indicator)
   - Performance indicators: green (<5s), yellow (5-15s), red (>15s)
   - Total cost summary: "Total actual cost: $0.48 (6 generations)"
   - Tooltip breakdown: "Prompt tokens: 234, Completion tokens: 222, Total: 456"

**Epic 4 Exit Criteria**:
- LLM providers integrated (OpenAI, Anthropic, Google)
- Model selection interface shows cost estimate: (models × prompt types)
- Parallel generation works for all checked prompt types
- Results displayed hierarchically: Prompt Type → Models
- Actual metadata (tokens, time, cost) shown per result
- Iteration workflow allows rapid testing

### Epic 5: Configuration Publishing & Production Integration (Weeks 13-14)

**Goal**: Enable publishing to production with validation and audit trails.

**Stories**:
1. ❌ **Story 5.1**: Pre-Publish Validation (All Prompt Types)
   - "Publish" button triggers validation for all 3 prompt types
   - Validation rules:
     - Shared: at least one API, section order defined, model selected
     - Per type: prompt not empty, at least one test generation for each checked type
   - Validation failure modal with checklist grouped by type
   - Warning if prompt changed without re-testing
   - Validation success enables "Confirm Publish" button

2. ❌ **Story 5.2**: Configuration Publishing with Confirmation (All Prompt Types)
   - Confirmation modal shows:
     - Trigger name
     - Configured APIs, section order, model (shared)
     - Per prompt type: truncated preview, character count, last tested timestamp
   - Expandable sections per type to view full prompt
   - Diff view if updating existing config (shows changes per type)
   - POST /api/triggers/:id/publish endpoint
   - Backend saves configuration to MongoDB with version number
   - Configuration marked as is_active = true
   - Success notification: "Published successfully with 3 prompt types as Version X.X"
   - "View Published Configuration" link

3. ❌ **Story 5.3**: Audit Logging and Change Tracking
   - All config changes logged to audit_log collection
   - Logged fields: user_id, action, timestamp, trigger_id, details (JSON diff)
   - Actions: created, updated, published, api_added, prompt_edited, model_changed
   - Backend middleware logs all write operations
   - Audit log UI (admin page, optional for MVP):
     - Table: timestamp, user, trigger, action, details
     - Filtering by trigger, user, date range, action
     - Export to CSV/JSON
   - Audit logs immutable (no deletion)

4. ❌ **Story 5.4**: Configuration Version History and Rollback
   - "Configuration History" screen (side-drawer)
   - List all published versions: version number, timestamp, user, "Active" badge
   - Click version → read-only view (APIs, prompt, model, section order)
   - "Compare with Another Version" button
   - Diff view: side-by-side comparison with highlighted changes
   - "Rollback to This Version" button
   - Rollback confirmation modal with warning
   - Rollback creates new version (not true revert)
   - Audit log entry created for rollback

5. ❌ **Story 5.5**: Production Integration and Active Configuration API
   - GET /api/triggers/:id/active-config endpoint
   - Returns currently active published configuration (all 3 prompt types)
   - Response includes: APIs, parser settings, section order, prompts (paid/unpaid/crawler), model config
   - API versioned (/api/v1/)
   - Cookie authentication required
   - Response cached (5-minute TTL)
   - 404 if no active config
   - OpenAPI documentation auto-generated
   - Integration test validates published config immediately accessible

**Epic 5 Exit Criteria**:
- Validation prevents publishing incomplete configs
- Publish confirmation shows all 3 prompt types with diff
- Audit log tracks all changes
- Version history accessible with rollback capability
- Active configuration API ready for existing news system integration

## Post-MVP Considerations

### Deferred Features (Not in MVP Scope)

**From PRD Checklist**:
- Full WCAG AA accessibility compliance (basic accessibility sufficient for MVP)
- Automated E2E testing (manual QA for MVP)
- Advanced monitoring dashboard (basic CloudWatch alerts sufficient)
- Comprehensive documentation (API docs auto-generated, user guide post-MVP)
- Competitive analysis detail (internal tool, low priority)

**Potential Phase 2 Enhancements**:
- Advanced data visualization (charts for cost tracking, performance analytics)
- Enhanced collaboration features (comments, approval workflow, real-time presence)
- Template system for prompts
- Bulk operations (publish multiple triggers at once)
- Keyboard shortcuts for power users
- High-contrast mode for accessibility
- Custom data sections (user-defined sections beyond 14 hardcoded)
- A/B testing framework for prompt variations
- Scheduled publishing (publish at specific time)
- Slack/email notifications for config changes

### Technical Debt to Address Post-MVP

**Known Shortcuts in MVP**:
- No containerization (Docker may improve deployment reliability)
- Synchronous generation (async with background jobs may improve UX for slow models)
- Manual E2E testing (automate critical paths post-MVP)
- Limited error recovery (circuit breakers, dead letter queues for production)
- No real-time collaboration (websockets for multi-user editing)

## Appendix - Useful Commands and Workflows

### Development Commands (To Be Documented in README)

**Backend**:
```bash
# Start development server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v

# Lint
flake8 app/

# Seed database
python scripts/seed_data.py

# Validate API keys
python scripts/test-api-keys.py
```

**Frontend**:
```bash
# Start development server
cd frontend
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint
npm run lint
```

**Full Stack**:
```bash
# Run both backend and frontend concurrently (using npm-run-all or similar)
npm run dev:all
```

### Deployment Commands (Story 1.6)

**Staging Deployment** (via CI/CD):
```bash
git push origin develop  # Triggers GitHub Actions → deploys to staging
```

**Production Deployment** (via CI/CD with manual approval):
```bash
git push origin main  # Triggers GitHub Actions → manual approval → deploys to production
```

**Manual Deployment** (if needed):
```bash
# SSH into EC2
ssh ec2-user@staging.news-cms.example.com

# Backend deployment
cd /var/www/news-cms/backend
git pull origin develop
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart news-cms-backend

# Frontend deployment (if SSR)
cd /var/www/news-cms/frontend
git pull origin develop
npm install
npm run build
sudo systemctl restart news-cms-frontend

# Check status
sudo systemctl status news-cms-backend
sudo systemctl status news-cms-frontend
```

### Debugging and Troubleshooting (Planned)

**Backend Logs**:
```bash
# Local
tail -f logs/app.log

# Production (CloudWatch)
aws logs tail /aws/news-cms/backend --follow
```

**Frontend Logs**:
```bash
# Local
npm run dev  # Logs to console

# Production
aws logs tail /aws/news-cms/frontend --follow
```

**MongoDB**:
```bash
# Connect to MongoDB
mongo mongodb://localhost:27017/news_cms_dev

# List collections
show collections

# Query triggers
db.triggers.find().pretty()

# Query active configurations
db.configurations.find({ is_active: true }).pretty()
```

**Common Issues** (To be documented as they arise):
- MongoDB connection timeout → Check AWS Security Group allows port 27017
- API key validation fails → Verify keys in Secrets Manager
- Frontend can't reach backend → Check Nginx config, CORS settings
- Generation timeout → Increase model timeout in config, check LLM API status

## Summary and Next Steps

### Current State Summary

**Phase**: Planning → Epic 1 Implementation Beginning

**Status**:
- ✅ PRD completed and reviewed (88% complete, nearly ready)
- ✅ UI/UX Specification v2.2 completed (multi-prompt type support)
- ⚠️ Story 1.5a in progress (Third-Party API Setup)
- ❌ No code written yet (greenfield project)
- ❌ Infrastructure not provisioned yet

**Key Documents**:
- [docs/prd.md](docs/prd.md) - Product Requirements (1185 lines)
- [docs/front-end-spec.md](docs/front-end-spec.md) - UI/UX Specification (1214 lines)
- [docs/architecture.md](docs/architecture.md) - This document

### Immediate Next Steps (Week 1)

**Story 1.5a Completion** (IN PROGRESS):
1. ✅ Complete API key acquisition:
   - OpenAI Team tier account ($20/month + usage)
   - Anthropic API access (application approval pending 1-2 days)
   - Google AI API key
2. ✅ Store all keys in AWS Secrets Manager
3. ✅ Configure billing alerts ($400 threshold)
4. ✅ Run test-api-keys.py successfully
5. ✅ Document setup process in docs/third-party-setup.md

**Critical Decision Required**:
- **Financial Data API Providers**: Product team must identify which providers to use (earnings data, price data, analyst ratings)
- **Impact**: Blocks Epic 2 (Data Pipeline) if not decided early
- **Owner**: Product team
- **Deadline**: End of Week 1

**Story 1.1 Kickoff** (Week 1):
- Create monorepo structure (frontend/, backend/)
- Initialize package.json and requirements.txt
- Configure development tooling (TypeScript, ESLint, pytest)
- Both apps run locally
- README.md with setup instructions

### Week 2-3 Plan (Epic 1 Continuation)

**Story 1.2**: MongoDB Database Setup
**Story 1.3**: Basic UI Shell
**Story 1.4**: Trigger Management Dashboard
**Story 1.6**: AWS Deployment to Staging

**Epic 1 Exit Goal**: Deployable walking skeleton with trigger selection by end of Week 3.

### Technical Investigations Required

**Before Epic 2**:
1. **Parser Integration Spike**:
   - Locate existing parser scripts in main platform
   - Document parser input/output interfaces
   - Decide: module import vs. subprocess execution
   - **Effort**: 1-2 days
   - **Owner**: Backend developer

2. **Authentication Integration Spike**:
   - Document existing auth system (cookie format, validation endpoint)
   - Design CMS integration approach
   - **Effort**: 1 day
   - **Owner**: Backend developer + platform team

**Before Epic 5**:
3. **Production Pipeline Integration Design**:
   - Understand existing news generation system architecture
   - Design configuration consumption pattern (MongoDB vs. REST API)
   - **Effort**: 1 day
   - **Owner**: Backend developer + platform team

### Success Metrics (From PRD)

**Usability Goals**:
- New users configure basic trigger in <30 minutes
- Iteration time (edit → regenerate → compare) <2 minutes
- Configuration creation to publication <2 hours

**Performance Goals** (NFRs):
- Page load <2 seconds (NFR1)
- Data API fetch <5 seconds per API (NFR2)
- News generation <30 seconds model-dependent (NFR3)
- Support 5-10 concurrent users without degradation (NFR4)

**Adoption Metrics** (Post-Launch):
- Active users per week
- Configurations published per week
- Reduction in developer time on content config tasks (target: 80%)
- User satisfaction (NPS)

### Risks and Mitigations

**Top 3 Risks** (from PRD):
1. **Parser Integration Complexity** (High likelihood, High impact)
   - Mitigation: Early spike, mock parsers for development
2. **LLM Cost Overruns** (Medium likelihood, Medium impact)
   - Mitigation: Cost tracking, spending limits ($500/month), mock mode
3. **Authentication Integration** (Medium likelihood, High impact)
   - Mitigation: Early investigation spike, fallback to simple JWT

**Schedule Risk**:
- **3-4 months for 26 stories = ~1.5-2 stories/week** (tight but achievable)
- **Recommendation**: Add 10-20% buffer for unknowns (PRD assessment)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-29
**Next Review**: End of Epic 1 (Week 3)

This architecture document will be updated as implementation progresses and technical decisions are made. All unknowns and risks should be resolved and documented in updates to this file.
