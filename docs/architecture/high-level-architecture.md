# High Level Architecture

## Project Type: Greenfield (New Development)

This is a **NEW internal tool** being built from scratch for the equity market research platform. While it will integrate with existing systems (parser scripts, authentication, production news generation pipeline), the CMS itself has no legacy code.

## Technical Summary

**Architecture Pattern**: Monolithic Application (No Microservices, No Containerization)

**Deployment Model**: Direct deployment to AWS EC2 with Nginx reverse proxy

**Development Status**: Planning phase → Epic 1 implementation beginning

## Planned Tech Stack

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

## Repository Structure Reality Check

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
