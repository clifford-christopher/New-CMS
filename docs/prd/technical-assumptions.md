# Technical Assumptions

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
