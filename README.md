# AI-Powered News CMS

A content management system for configuring and testing AI-generated financial news for equity market research.

## Project Overview

The AI-Powered News CMS is an internal tool that enables content managers and analysts to:

- Configure trigger-based news generation (earnings alerts, price movements, etc.)
- Select and manage financial data sources and sections
- Create and test prompt templates for multiple content types (paid, unpaid, crawler)
- Test news generation across multiple LLM providers (OpenAI, Anthropic, Google AI)
- Compare and refine results before publishing to production
- Publish configurations with version control and audit trails

## Tech Stack

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI (REST API with auto-generated OpenAPI docs)
- **Database**: MongoDB (Motor async driver)
- **Validation**: Pydantic v2
- **Cloud**: AWS (EC2, Secrets Manager)
- **LLM Providers**: OpenAI, Anthropic, Google AI

### Frontend
- **Runtime**: Node.js 18.x LTS
- **Framework**: Next.js 14+ (App Router with TypeScript)
- **UI Library**: React-Bootstrap (Bootstrap 5)
- **Code Editor**: Monaco Editor (for prompt editing)
- **State Management**: React Context API

## Project Structure

```
news-cms/
├── backend/              # Python/FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI entry point
│   │   ├── models/       # Pydantic data models
│   │   ├── routers/      # API route handlers
│   │   ├── services/     # Business logic
│   │   ├── data_adapters/  # Financial data API integrations
│   │   ├── parsers/      # Parser script integration
│   │   └── llm_providers/  # LLM abstraction layer
│   ├── tests/            # pytest test suite
│   ├── requirements.txt  # Python dependencies
│   └── pyproject.toml    # Python project config
├── frontend/             # Next.js/React frontend
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components
│   │   ├── contexts/     # React Context providers
│   │   ├── lib/          # Utility functions
│   │   └── types/        # TypeScript types
│   ├── public/           # Static assets
│   ├── package.json
│   └── tsconfig.json
├── scripts/              # Utility scripts
│   └── test-api-keys.py  # API key validation
├── docs/                 # Project documentation
│   ├── prd.md            # Product Requirements
│   ├── front-end-spec.md # UI/UX Specification
│   └── architecture.md   # Architecture Document
└── README.md             # This file
```

## Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x LTS or higher
- **MongoDB**: Community Edition 5.0+ (local) OR MongoDB Atlas account
- **AWS Account**: For Secrets Manager (API keys storage)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd news-cms
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp ../.env.example .env

# Edit .env with your local MongoDB URI and AWS credentials
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Frontend uses NEXT_PUBLIC_API_URL from .env.example
```

#### 4. Environment Configuration

Create a `.env` file in the root directory (copy from `.env.example`):

```bash
# Backend
MONGODB_URI=mongodb://localhost:27017/news_cms_dev
AWS_REGION=us-east-1
AWS_SECRETS_MANAGER_PREFIX=news-cms/

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Application

#### Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**

API Documentation (Swagger): **http://localhost:8000/docs**

#### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:3000**

### Verify Installation

1. **Backend**: Visit http://localhost:8000 - should return JSON with status
2. **Frontend**: Visit http://localhost:3000 - should display dashboard page
3. **API Docs**: Visit http://localhost:8000/docs - should show Swagger UI

## Development Workflow

### Backend Development

```bash
cd backend

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Linting
flake8 app/

# Format code
black app/
isort app/

# Type checking
mypy app/
```

### Frontend Development

```bash
cd frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

## Project Status

**Current Phase**: Epic 1 - Foundation & Core Infrastructure

**Completed**:
- ✅ Story 1.1: Project Setup and Monorepo Structure

**In Progress**:
- ⚠️ Story 1.5a: Third-Party API Setup (API keys configuration)

**Next Steps**:
- Story 1.2: MongoDB Database Setup and Connection
- Story 1.3: Basic UI Shell and Navigation
- Story 1.4: Trigger Management Dashboard
- Story 1.6: AWS Deployment Setup

## Key Documents

- **[PRD](docs/prd.md)**: Complete product requirements and epic breakdown (1185 lines)
- **[Architecture Document](docs/architecture.md)**: Technical architecture and implementation roadmap (1303 lines)
- **[Frontend Specification](docs/front-end-spec.md)**: Detailed UI/UX design (1214 lines)

## Epic Roadmap

1. **Epic 1: Foundation & Core Infrastructure** (Weeks 1-3)
   - Project setup, MongoDB, basic UI, trigger dashboard, AWS deployment

2. **Epic 2: Data Pipeline & Integration** (Weeks 4-6)
   - API configuration, data retrieval, parser integration

3. **Epic 3: Prompt Engineering Workspace** (Weeks 7-9)
   - Section reordering, tabbed prompt editor, validation, version history

4. **Epic 4: Multi-Model Generation & Testing** (Weeks 10-12)
   - LLM integration, model selection, parallel generation, result comparison

5. **Epic 5: Configuration Publishing & Production Integration** (Weeks 13-14)
   - Pre-publish validation, audit logging, version history, production API

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests (Coming in later epics)

```bash
cd frontend
npm test
```

## Deployment

Deployment is configured for AWS EC2 with Nginx reverse proxy (Story 1.6).

See [Architecture Document](docs/architecture.md#deployment-process) for detailed deployment instructions.

## API Keys & Secrets

**IMPORTANT**: Never commit API keys or secrets to git.

All secrets are stored in AWS Secrets Manager:
- `news-cms/llm/openai/api-key`
- `news-cms/llm/anthropic/api-key`
- `news-cms/llm/google/api-key`
- `news-cms/db/mongodb-uri`

Use `scripts/test-api-keys.py` to validate API key setup.

## Contributing

This is an internal project. Follow the team's development workflow:

1. Create feature branch from `develop`
2. Make changes following code style guidelines
3. Write tests for new functionality
4. Run linters and tests
5. Create pull request to `develop`
6. After review and approval, merge to `develop`
7. `develop` auto-deploys to staging
8. After QA approval, merge to `main` for production

## Support

For questions or issues:
- Check [Architecture Document](docs/architecture.md) for technical details
- Check [PRD](docs/prd.md) for product requirements
- Contact the development team

## License

Internal use only - All rights reserved

---

**Version**: 1.0.0
**Last Updated**: 2025-10-29
**Epic**: 1 - Foundation & Core Infrastructure
**Story**: 1.1 - Project Setup Complete
